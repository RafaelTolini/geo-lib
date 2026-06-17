"""Formatted restart keyword reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.domain.restart.restart_dataset import RestartDataset
from reservoir_data.domain.restart.restart_header import RestartHeader
from reservoir_data.domain.restart.restart_report import RestartReport
from reservoir_data.exceptions.errors import FileReadError, ParseError
from reservoir_data.formats.grdecl.parser import GrdeclParser
from reservoir_data.formats.grdecl.tokenizer import (
    GrdeclToken,
    GrdeclTokenKind,
)
from reservoir_data.schemas.detection import FormatDetectionResult


TokenRecord = tuple[GrdeclToken, ...]


@dataclass(frozen=True, slots=True)
class _RestartBlock:
    report_record: TokenRecord | None
    payload_records: tuple[TokenRecord, ...]


@dataclass(frozen=True, slots=True)
class FormattedRestartReader:
    """Read formatted restart files using GRDECL-style keyword syntax.

    A unified formatted fixture contains one or more report blocks starting with
    a `REPORT` keyword. A non-unified formatted report-step file may either use
    one `REPORT` block or omit `REPORT` and rely on the detected report step from
    its filename. Payload keywords are parsed lazily when the report is accessed.
    """

    parser: GrdeclParser = field(default_factory=GrdeclParser)
    encoding: str = "utf-8"

    def read(
        self,
        path: str | Path,
        detection: FormatDetectionResult | None = None,
    ) -> RestartDataset:
        """Read and index a formatted restart file."""

        source_path = Path(path)
        try:
            data = source_path.read_bytes()
        except OSError as error:
            raise FileReadError(
                f"Could not read restart file {source_path}: {error}"
            ) from error
        return self.parse_bytes(data, source=str(source_path), detection=detection)

    def parse_bytes(
        self,
        data: bytes,
        source: str | None = None,
        detection: FormatDetectionResult | None = None,
    ) -> RestartDataset:
        """Decode and index formatted restart data."""

        if b"\x00" in data:
            raise ParseError(
                "Formatted restart reader received binary-looking data; "
                "binary restart keyword decoding is not implemented"
            )
        try:
            text = data.decode(self.encoding)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Could not decode formatted restart data as {self.encoding}"
            ) from error
        return self.parse_text(text, source=source, detection=detection)

    def parse_text(
        self,
        text: str,
        source: str | None = None,
        detection: FormatDetectionResult | None = None,
    ) -> RestartDataset:
        """Index formatted restart text without parsing report payloads."""

        if "\x00" in text:
            raise ParseError(
                "Formatted restart reader received binary-looking text; "
                "binary restart keyword decoding is not implemented"
            )

        records = self._split_records(tuple(self.parser.tokenizer.iter_tokens(text)))
        blocks = self._split_blocks(records, detection)
        reports = tuple(
            self._report_from_block(block, sequence_index, source, detection)
            for sequence_index, block in enumerate(blocks)
        )
        return RestartDataset(
            reports=reports,
            sources=(() if source is None else (source,)),
            unified=None if detection is None else detection.unified,
        )

    def _split_records(
        self, tokens: tuple[GrdeclToken, ...]
    ) -> tuple[TokenRecord, ...]:
        records: list[TokenRecord] = []
        current: list[GrdeclToken] = []
        for token in tokens:
            current.append(token)
            if token.kind is GrdeclTokenKind.TERMINATOR:
                records.append(tuple(current))
                current = []
        if current:
            raise ParseError(
                f"Unterminated restart keyword record starting with {current[0].text!r}"
            )
        if not records:
            raise ParseError("Restart file contains no keyword records")
        return tuple(records)

    def _split_blocks(
        self,
        records: tuple[TokenRecord, ...],
        detection: FormatDetectionResult | None,
    ) -> tuple[_RestartBlock, ...]:
        report_indices = [
            index
            for index, record in enumerate(records)
            if record and record[0].text.strip().upper() == "REPORT"
        ]

        if not report_indices:
            if detection is not None and detection.report_step is not None:
                return (_RestartBlock(report_record=None, payload_records=records),)
            raise ParseError("Restart file is missing required REPORT keyword")

        if report_indices[0] != 0:
            raise ParseError("Restart records before first REPORT are not supported")

        blocks: list[_RestartBlock] = []
        for position, start in enumerate(report_indices):
            end = (
                report_indices[position + 1]
                if position + 1 < len(report_indices)
                else len(records)
            )
            blocks.append(
                _RestartBlock(
                    report_record=records[start],
                    payload_records=tuple(records[start + 1 : end]),
                )
            )
        return tuple(blocks)

    def _report_from_block(
        self,
        block: _RestartBlock,
        sequence_index: int,
        source: str | None,
        detection: FormatDetectionResult | None,
    ) -> RestartReport:
        header = self._header_from_block(block, sequence_index, source, detection)
        payload_records = block.payload_records

        def load_payload(
            records: tuple[TokenRecord, ...] = payload_records,
        ) -> KeywordDataset:
            return self._parse_payload(records, source)

        return RestartReport(header=header, _keyword_loader=load_payload)

    def _header_from_block(
        self,
        block: _RestartBlock,
        sequence_index: int,
        source: str | None,
        detection: FormatDetectionResult | None,
    ) -> RestartHeader:
        detected_step = None if detection is None else detection.report_step
        step = detected_step
        simulation_days: float | None = None
        report_date: date | None = None

        if block.report_record is not None:
            report_dataset = self.parser.parse_tokens(
                block.report_record,
                source=source,
            )
            report_record = report_dataset.record("REPORT")
            if report_record is None:
                raise ParseError("Internal error: REPORT block missing REPORT record")
            values = report_record.values
            parsed_step = self._optional_integer(values, 0, "REPORT")
            if parsed_step is not None:
                if detected_step is not None and detected_step != parsed_step:
                    raise ParseError(
                        f"REPORT step {parsed_step} does not match detected "
                        f"report step {detected_step}"
                    )
                step = parsed_step
            simulation_days = self._optional_float(values, 1, "REPORT")
            report_date = self._optional_date(values, 2, "REPORT")

        if step is None:
            raise ParseError("Restart report step is not available")

        return RestartHeader(
            report_step=step,
            sequence_index=sequence_index,
            simulation_days=simulation_days,
            report_date=report_date,
            source=source,
            unified=None if detection is None else detection.unified,
        )

    def _parse_payload(
        self, payload_records: tuple[TokenRecord, ...], source: str | None
    ) -> KeywordDataset:
        if not payload_records:
            return KeywordDataset(records=(), source=source)
        tokens: list[GrdeclToken] = []
        for record in payload_records:
            tokens.extend(record)
        return self.parser.parse_tokens(tuple(tokens), source=source)

    def _optional_integer(
        self, values: tuple[KeywordValue, ...], index: int, keyword_name: str
    ) -> int | None:
        if index >= len(values):
            return None
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ParseError(
                f"{keyword_name} value {index} must be an integer, got {value!r}"
            )
        return value

    def _optional_float(
        self, values: tuple[KeywordValue, ...], index: int, keyword_name: str
    ) -> float | None:
        if index >= len(values):
            return None
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ParseError(
                f"{keyword_name} value {index} must be numeric, got {value!r}"
            )
        return float(value)

    def _optional_date(
        self, values: tuple[KeywordValue, ...], index: int, keyword_name: str
    ) -> date | None:
        if index >= len(values):
            return None
        value = values[index]
        if not isinstance(value, str):
            raise ParseError(
                f"{keyword_name} value {index} must be an ISO date string, got "
                f"{value!r}"
            )
        try:
            return date.fromisoformat(value)
        except ValueError as error:
            raise ParseError(
                f"{keyword_name} value {index} is not a valid ISO date: {value!r}"
            ) from error
