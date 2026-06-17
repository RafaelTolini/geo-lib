"""Formatted RFT/PLT reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.domain.rft.rft_cell_measurement import RftCellMeasurement
from reservoir_data.domain.rft.rft_dataset import RftDataset
from reservoir_data.domain.rft.rft_record import RftRecord
from reservoir_data.exceptions.errors import FileReadError, ParseError
from reservoir_data.formats.grdecl.parser import GrdeclParser
from reservoir_data.formats.grdecl.tokenizer import GrdeclToken, GrdeclTokenKind
from reservoir_data.schemas.detection import FormatDetectionResult


TokenRecord = tuple[GrdeclToken, ...]


@dataclass(frozen=True, slots=True)
class _RftBlock:
    header_record: TokenRecord
    measurement_records: tuple[TokenRecord, ...]
    source: str | None
    default_type: str


@dataclass(frozen=True, slots=True)
class FormattedRftReader:
    """Read scoped GRDECL-style formatted RFT/PLT files."""

    parser: GrdeclParser = field(default_factory=GrdeclParser)
    encoding: str = "utf-8"

    def read(
        self,
        detections: tuple[FormatDetectionResult, ...],
        grid: ReservoirGrid | None = None,
    ) -> RftDataset:
        """Read and index formatted RFT/PLT detections."""

        records: list[RftRecord] = []
        sources: list[str] = []
        for detection in detections:
            source = str(detection.path)
            blocks = self._blocks_from_path(detection.path, detection)
            records.extend(self._record_from_block(block, grid) for block in blocks)
            sources.append(source)
        return RftDataset(records=tuple(records), sources=tuple(sources))

    def _blocks_from_path(
        self,
        path: str | Path,
        detection: FormatDetectionResult,
    ) -> tuple[_RftBlock, ...]:
        source_path = Path(path)
        try:
            data = source_path.read_bytes()
        except OSError as error:
            raise FileReadError(f"Could not read RFT/PLT file {source_path}: {error}") from error
        text = self._decode_bytes(data)
        records = self._split_records(tuple(self.parser.tokenizer.iter_tokens(text)))
        default_type = (
            "PLT" if detection.file_category is FileCategory.PLT else "RFT"
        )
        return self._split_blocks(records, str(source_path), default_type)

    def _split_blocks(
        self,
        records: tuple[TokenRecord, ...],
        source: str | None,
        default_type: str,
    ) -> tuple[_RftBlock, ...]:
        header_indices = [
            index
            for index, record in enumerate(records)
            if self._record_is(record, "RFTREC")
        ]
        if not header_indices:
            raise ParseError("Formatted RFT/PLT file is missing RFTREC records")
        if header_indices[0] != 0:
            raise ParseError("RFT/PLT measurement records before RFTREC are invalid")

        blocks: list[_RftBlock] = []
        for position, start in enumerate(header_indices):
            end = (
                header_indices[position + 1]
                if position + 1 < len(header_indices)
                else len(records)
            )
            blocks.append(
                _RftBlock(
                    header_record=records[start],
                    measurement_records=tuple(records[start + 1 : end]),
                    source=source,
                    default_type=default_type,
                )
            )
        return tuple(blocks)

    def _record_from_block(
        self,
        block: _RftBlock,
        grid: ReservoirGrid | None,
    ) -> RftRecord:
        parsed_header = self.parser.parse_tokens(
            block.header_record,
            source=block.source,
        ).record("RFTREC")
        values = parsed_header.values
        well_name = self._required_string(values, 0, "RFTREC").upper()
        report_date = self._required_date(values, 1, "RFTREC")
        record_type = (
            self._optional_string(values, 2, "RFTREC") or block.default_type
        ).upper()
        measurement_records = block.measurement_records

        def load_measurements(
            records: tuple[TokenRecord, ...] = measurement_records,
        ) -> tuple[RftCellMeasurement, ...]:
            return self._measurements_from_records(records, block.source, grid)

        return RftRecord(
            well_name=well_name,
            report_date=report_date,
            record_type=record_type,
            _measurement_loader=load_measurements,
            source=block.source,
        )

    def _measurements_from_records(
        self,
        records: tuple[TokenRecord, ...],
        source: str | None,
        grid: ReservoirGrid | None,
    ) -> tuple[RftCellMeasurement, ...]:
        if not records:
            raise ParseError("RFT/PLT record contains no measurement rows")
        return tuple(self._measurement_from_record(record, source, grid) for record in records)

    def _measurement_from_record(
        self,
        record: TokenRecord,
        source: str | None,
        grid: ReservoirGrid | None,
    ) -> RftCellMeasurement:
        record_name = record[0].text.strip().upper()
        if record_name not in {"RFTCELL", "PLTCELL"}:
            raise ParseError(f"Unsupported RFT/PLT measurement record: {record_name}")
        parsed = self.parser.parse_tokens(record, source=source).record(record_name)
        values = parsed.values
        cell = CellIndex.ijk(
            self._required_integer(values, 0, record_name),
            self._required_integer(values, 1, record_name),
            self._required_integer(values, 2, record_name),
            simulator_one_based=True,
        )
        if grid is not None:
            grid.global_index(cell)
        depth = self._required_float(values, 3, record_name)
        pressure = self._required_float(values, 4, record_name)
        if record_name == "RFTCELL":
            saturations = self._rft_saturations(values, record_name)
            return RftCellMeasurement(
                cell=cell,
                depth=depth,
                pressure=pressure,
                saturations=saturations,
            )
        return RftCellMeasurement(
            cell=cell,
            depth=depth,
            pressure=pressure,
            rates=self._plt_rates(values, record_name),
        )

    def _rft_saturations(
        self,
        values: tuple[KeywordValue, ...],
        record_name: str,
    ) -> dict[str, float]:
        saturations: dict[str, float] = {}
        if len(values) > 5:
            saturations["WATER"] = self._required_float(values, 5, record_name)
        if len(values) > 6:
            saturations["OIL"] = self._required_float(values, 6, record_name)
        if len(values) > 7:
            saturations["GAS"] = self._required_float(values, 7, record_name)
        return saturations

    def _plt_rates(
        self,
        values: tuple[KeywordValue, ...],
        record_name: str,
    ) -> dict[str, float]:
        return {
            "OIL": self._required_float(values, 5, record_name),
            "WATER": self._required_float(values, 6, record_name),
            "GAS": self._required_float(values, 7, record_name),
        }

    def _decode_bytes(self, data: bytes) -> str:
        if b"\x00" in data:
            raise ParseError(
                "Formatted RFT/PLT reader received binary-looking data; "
                "binary RFT/PLT decoding is not implemented"
            )
        try:
            return data.decode(self.encoding)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Could not decode formatted RFT/PLT data as {self.encoding}"
            ) from error

    def _split_records(
        self,
        tokens: tuple[GrdeclToken, ...],
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
                f"Unterminated RFT/PLT keyword record starting with {current[0].text!r}"
            )
        if not records:
            raise ParseError("RFT/PLT file contains no keyword records")
        return tuple(records)

    def _record_is(self, record: TokenRecord, name: str) -> bool:
        return bool(record) and record[0].text.strip().upper() == name

    def _required_string(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> str:
        if index >= len(values) or not isinstance(values[index], str):
            raise ParseError(f"{keyword_name} value {index} must be a string")
        value = values[index].strip()
        if not value:
            raise ParseError(f"{keyword_name} value {index} must not be empty")
        return value

    def _optional_string(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> str | None:
        if index >= len(values):
            return None
        return self._required_string(values, index, keyword_name)

    def _required_integer(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> int:
        if index >= len(values):
            raise ParseError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ParseError(
                f"{keyword_name} value {index} must be an integer, got {value!r}"
            )
        return value

    def _required_float(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> float:
        if index >= len(values):
            raise ParseError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ParseError(
                f"{keyword_name} value {index} must be numeric, got {value!r}"
            )
        return float(value)

    def _required_date(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> date:
        raw_value = self._required_string(values, index, keyword_name)
        try:
            return date.fromisoformat(raw_value)
        except ValueError as error:
            raise ParseError(
                f"{keyword_name} value {index} is not a valid ISO date: {raw_value!r}"
            ) from error
