"""Formatted summary keyword reader."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.domain.summary.summary_dataset import SummaryDataset
from reservoir_data.domain.summary.summary_key import SummaryKey
from reservoir_data.domain.summary.summary_metadata import (
    SummaryMetadata,
    SummaryVectorMetadata,
)
from reservoir_data.domain.summary.summary_vector import SummaryVector
from reservoir_data.exceptions.errors import FileReadError, ParseError, SummaryDataError
from reservoir_data.formats.grdecl.parser import GrdeclParser
from reservoir_data.formats.grdecl.tokenizer import GrdeclToken, GrdeclTokenKind
from reservoir_data.infrastructure.caching.json_index_cache import JsonIndexCache
from reservoir_data.schemas.detection import FormatDetectionResult


TokenRecord = tuple[GrdeclToken, ...]


@dataclass(frozen=True, slots=True)
class _DataAxis:
    simulation_days: tuple[float, ...]
    report_steps: tuple[int, ...]
    dates: tuple[date, ...]


@dataclass(frozen=True, slots=True)
class _DataVectorRecord:
    canonical_key: str
    tokens: TokenRecord
    axis_length: int
    source: str | None


@dataclass(frozen=True, slots=True)
class _DataSource:
    records: tuple[TokenRecord, ...]
    source: str | None
    detection: FormatDetectionResult | None


@dataclass(frozen=True, slots=True)
class FormattedSummaryReader:
    """Read scoped GRDECL-style formatted summary metadata and values.

    Metadata files use `VECTOR` records:

    `VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /`
    `VECTOR 'WOPR' 'SM3/DAY' 'WELL' 'PROD-1' /`

    Data files use eager time-axis records plus lazy value records:

    `TIME 0 30 /`
    `DATES '2026-01-01' '2026-01-31' /`
    `REPORTS 0 1 /`
    `VALUES 'FOPR' 100 120 /`
    `VALUES 'WOPR:PROD-1' 40 50 /`
    """

    parser: GrdeclParser = field(default_factory=GrdeclParser)
    encoding: str = "utf-8"

    def read(
        self,
        metadata_path: str | Path,
        data_detections: tuple[FormatDetectionResult, ...],
        cache: JsonIndexCache | None = None,
    ) -> SummaryDataset:
        """Read formatted summary metadata and data files."""

        metadata_source = str(metadata_path)
        source_paths = (
            Path(metadata_path),
            *(detection.path for detection in data_detections),
        )
        cache_key = self._cache_key(metadata_path, data_detections)
        if cache is not None:
            cached = cache.load("formatted-summary-index", cache_key, source_paths)
            if cached is not None:
                return self._dataset_from_cache_payload(cached)

        metadata_records = self._records_from_path(metadata_path)
        data_sources = tuple(
            _DataSource(
                records=self._records_from_path(detection.path),
                source=str(detection.path),
                detection=detection,
            )
            for detection in data_detections
        )
        dataset = self._dataset_from_records(
            metadata_records=metadata_records,
            metadata_source=metadata_source,
            data_sources=data_sources,
        )
        if cache is not None:
            cache.save(
                "formatted-summary-index",
                cache_key,
                source_paths,
                self._cache_payload_from_records(
                    metadata_records=metadata_records,
                    metadata_source=metadata_source,
                    data_sources=data_sources,
                ),
            )
        return dataset

    def _dataset_from_records(
        self,
        metadata_records: tuple[TokenRecord, ...],
        metadata_source: str | None,
        data_sources: tuple[_DataSource, ...],
    ) -> SummaryDataset:
        metadata = self._parse_metadata(metadata_records, metadata_source)
        if not data_sources:
            raise FileReadError("No summary data files were provided")

        simulation_days: list[float] = []
        report_steps: list[int] = []
        dates: list[date] = []
        vector_records_by_key: dict[str, list[_DataVectorRecord]] = {
            key: [] for key in metadata.keys()
        }

        for data_source in data_sources:
            axis = self._parse_axis(
                data_source.records,
                data_source.source,
                data_source.detection,
            )
            simulation_days.extend(axis.simulation_days)
            report_steps.extend(axis.report_steps)
            dates.extend(axis.dates)
            for vector_record in self._index_vector_records(
                data_source.records,
                axis_length=len(axis.simulation_days),
                source=data_source.source,
            ):
                vector_records_by_key.setdefault(vector_record.canonical_key, []).append(
                    vector_record
                )

        if len(set(report_steps)) != len(report_steps):
            raise SummaryDataError("Summary data contains duplicate report steps")

        loaders = {
            item.key.canonical: self._make_vector_loader(
                metadata=item,
                vector_records=tuple(vector_records_by_key.get(item.key.canonical, ())),
                simulation_days=tuple(simulation_days),
                report_steps=tuple(report_steps),
                dates=tuple(dates),
            )
            for item in metadata.vectors
        }
        unified = self._unified_flag(data_sources)
        sources = tuple(
            source
            for source in (
                metadata_source,
                *(data_source.source for data_source in data_sources),
            )
            if source is not None
        )
        return SummaryDataset(
            metadata=metadata,
            simulation_days=tuple(simulation_days),
            report_steps=tuple(report_steps),
            dates=tuple(dates),
            _vector_loaders=loaders,
            sources=sources,
            unified=unified,
        )

    def _dataset_from_cache_payload(
        self,
        payload: dict[str, object],
    ) -> SummaryDataset:
        metadata = self._metadata_from_cache_payload(payload)
        data_sources = self._data_sources_from_cache_payload(payload)
        simulation_days: list[float] = []
        report_steps: list[int] = []
        dates: list[date] = []
        for data_source in data_sources:
            simulation_days.extend(data_source["simulation_days"])
            report_steps.extend(data_source["report_steps"])
            dates.extend(data_source["dates"])

        loaders = {
            item.key.canonical: self._make_cached_vector_loader(
                metadata=item,
                data_sources=data_sources,
                simulation_days=tuple(simulation_days),
                report_steps=tuple(report_steps),
                dates=tuple(dates),
            )
            for item in metadata.vectors
        }
        sources = tuple(str(source) for source in payload.get("sources", ()))
        unified_value = payload.get("unified")
        unified = unified_value if isinstance(unified_value, bool) else None
        return SummaryDataset(
            metadata=metadata,
            simulation_days=tuple(simulation_days),
            report_steps=tuple(report_steps),
            dates=tuple(dates),
            _vector_loaders=loaders,
            sources=sources,
            unified=unified,
        )

    def _metadata_from_cache_payload(
        self,
        payload: dict[str, object],
    ) -> SummaryMetadata:
        raw_vectors = payload.get("metadata")
        if not isinstance(raw_vectors, list):
            raise SummaryDataError("Cached summary metadata is malformed")
        vector_metadata: list[SummaryVectorMetadata] = []
        for item in raw_vectors:
            if not isinstance(item, dict):
                raise SummaryDataError("Cached summary vector metadata is malformed")
            vector_metadata.append(
                SummaryVectorMetadata(
                    key=SummaryKey(
                        keyword=str(item["keyword"]),
                        qualifier=(
                            None
                            if item.get("qualifier") is None
                            else str(item.get("qualifier"))
                        ),
                        qualifier_kind=(
                            None
                            if item.get("qualifier_kind") is None
                            else str(item.get("qualifier_kind"))
                        ),
                    ),
                    unit=None if item.get("unit") is None else str(item.get("unit")),
                    classification=(
                        None
                        if item.get("classification") is None
                        else str(item.get("classification"))
                    ),
                )
            )
        source = payload.get("metadata_source")
        return SummaryMetadata(
            vectors=tuple(vector_metadata),
            source=None if source is None else str(source),
        )

    def _data_sources_from_cache_payload(
        self,
        payload: dict[str, object],
    ) -> tuple[dict[str, object], ...]:
        raw_sources = payload.get("data_sources")
        if not isinstance(raw_sources, list):
            raise SummaryDataError("Cached summary data sources are malformed")
        data_sources: list[dict[str, object]] = []
        for item in raw_sources:
            if not isinstance(item, dict):
                raise SummaryDataError("Cached summary data source is malformed")
            source = str(item["source"])
            simulation_days = tuple(float(value) for value in item["simulation_days"])
            report_steps = tuple(int(value) for value in item["report_steps"])
            dates = tuple(date.fromisoformat(str(value)) for value in item["dates"])
            vector_keys = tuple(str(value) for value in item["vector_keys"])
            data_sources.append(
                {
                    "source": source,
                    "simulation_days": simulation_days,
                    "report_steps": report_steps,
                    "dates": dates,
                    "vector_keys": vector_keys,
                }
            )
        return tuple(data_sources)

    def _parse_metadata(
        self,
        records: tuple[TokenRecord, ...],
        source: str | None,
    ) -> SummaryMetadata:
        vector_metadata: list[SummaryVectorMetadata] = []
        for record in records:
            if not self._record_is(record, "VECTOR"):
                raise SummaryDataError(
                    "Formatted summary metadata supports VECTOR records only"
                )
            parsed = self.parser.parse_tokens(record, source=source).record("VECTOR")
            values = parsed.values
            keyword = self._required_string(values, 0, "VECTOR")
            unit = self._required_string(values, 1, "VECTOR")
            classification = self._required_string(values, 2, "VECTOR")
            qualifier = self._optional_string(values, 3, "VECTOR")
            key = SummaryKey(
                keyword=keyword,
                qualifier=qualifier,
                qualifier_kind=None if qualifier is None else classification,
            )
            vector_metadata.append(
                SummaryVectorMetadata(
                    key=key,
                    unit=unit,
                    classification=classification,
                )
            )
        return SummaryMetadata(vectors=tuple(vector_metadata), source=source)

    def _parse_axis(
        self,
        records: tuple[TokenRecord, ...],
        source: str | None,
        detection: FormatDetectionResult | None,
    ) -> _DataAxis:
        time_record = self._first_record(records, "TIME") or self._first_record(
            records,
            "DAYS",
        )
        date_record = self._first_record(records, "DATES")
        report_record = self._first_record(records, "REPORTS")
        if time_record is None:
            raise SummaryDataError("Summary data is missing TIME axis")
        if date_record is None:
            raise SummaryDataError("Summary data is missing DATES axis")

        simulation_days = self._numeric_axis(time_record, source)
        dates = self._date_axis(date_record, source)
        if report_record is None:
            detected_step = None if detection is None else detection.report_step
            if detected_step is None or len(simulation_days) != 1:
                raise SummaryDataError(
                    "Summary data is missing REPORTS axis and no single detected "
                    "report step is available"
                )
            report_steps = (detected_step,)
        else:
            report_steps = self._integer_axis(report_record, source)

        if not (
            len(simulation_days) == len(dates) == len(report_steps)
        ):
            raise SummaryDataError("Summary time-axis record lengths do not match")
        return _DataAxis(
            simulation_days=simulation_days,
            report_steps=report_steps,
            dates=dates,
        )

    def _index_vector_records(
        self,
        records: tuple[TokenRecord, ...],
        axis_length: int,
        source: str | None,
    ) -> tuple[_DataVectorRecord, ...]:
        indexed: list[_DataVectorRecord] = []
        for record in records:
            if not self._record_is(record, "VALUES"):
                continue
            if len(record) < 3:
                raise SummaryDataError("VALUES record must include a vector key")
            canonical_key = SummaryKey.parse(record[1].text).canonical
            indexed.append(
                _DataVectorRecord(
                    canonical_key=canonical_key,
                    tokens=record,
                    axis_length=axis_length,
                    source=source,
                )
            )
        return tuple(indexed)

    def _make_vector_loader(
        self,
        metadata: SummaryVectorMetadata,
        vector_records: tuple[_DataVectorRecord, ...],
        simulation_days: tuple[float, ...],
        report_steps: tuple[int, ...],
        dates: tuple[date, ...],
    ) -> Callable[[], SummaryVector]:
        def load_vector() -> SummaryVector:
            values: list[float] = []
            if not vector_records:
                raise SummaryDataError(
                    f"Summary vector {metadata.key.canonical!r} has no data records"
                )
            for vector_record in vector_records:
                values.extend(
                    self._values_from_vector_record(
                        vector_record,
                        expected_key=metadata.key.canonical,
                    )
                )
            if len(values) != len(simulation_days):
                raise SummaryDataError(
                    f"Summary vector {metadata.key.canonical!r} has {len(values)} "
                    f"values; expected {len(simulation_days)}"
                )
            return SummaryVector(
                key=metadata.key,
                values=tuple(values),
                simulation_days=simulation_days,
                report_steps=report_steps,
                dates=dates,
                unit=metadata.unit,
            )

        return load_vector

    def _make_cached_vector_loader(
        self,
        metadata: SummaryVectorMetadata,
        data_sources: tuple[dict[str, object], ...],
        simulation_days: tuple[float, ...],
        report_steps: tuple[int, ...],
        dates: tuple[date, ...],
    ) -> Callable[[], SummaryVector]:
        def load_vector() -> SummaryVector:
            values: list[float] = []
            for data_source in data_sources:
                vector_keys = data_source["vector_keys"]
                if metadata.key.canonical not in vector_keys:
                    continue
                values.extend(
                    self._values_from_path_for_key(
                        Path(str(data_source["source"])),
                        metadata.key.canonical,
                        len(data_source["simulation_days"]),
                    )
                )
            if len(values) != len(simulation_days):
                raise SummaryDataError(
                    f"Summary vector {metadata.key.canonical!r} has {len(values)} "
                    f"values; expected {len(simulation_days)}"
                )
            return SummaryVector(
                key=metadata.key,
                values=tuple(values),
                simulation_days=simulation_days,
                report_steps=report_steps,
                dates=dates,
                unit=metadata.unit,
            )

        return load_vector

    def _values_from_vector_record(
        self,
        vector_record: _DataVectorRecord,
        expected_key: str,
    ) -> tuple[float, ...]:
        parsed = self.parser.parse_tokens(
            vector_record.tokens,
            source=vector_record.source,
        ).record("VALUES")
        values = parsed.values
        raw_key = self._required_string(values, 0, "VALUES")
        canonical_key = SummaryKey.parse(raw_key).canonical
        if canonical_key != expected_key:
            raise SummaryDataError(
                f"VALUES record for {canonical_key!r} was loaded as {expected_key!r}"
            )
        numeric_values = tuple(
            self._required_number(values, index, "VALUES")
            for index in range(1, len(values))
        )
        if len(numeric_values) != vector_record.axis_length:
            raise SummaryDataError(
                f"Summary vector {expected_key!r} has {len(numeric_values)} values "
                f"in {vector_record.source}; expected {vector_record.axis_length}"
            )
        return numeric_values

    def _values_from_path_for_key(
        self,
        path: Path,
        key: str,
        axis_length: int,
    ) -> tuple[float, ...]:
        records = self._records_from_path(path)
        for vector_record in self._index_vector_records(
            records,
            axis_length=axis_length,
            source=str(path),
        ):
            if vector_record.canonical_key == key:
                return self._values_from_vector_record(
                    vector_record,
                    expected_key=key,
                )
        raise SummaryDataError(f"Summary vector {key!r} has no data records")

    def _cache_payload_from_records(
        self,
        metadata_records: tuple[TokenRecord, ...],
        metadata_source: str | None,
        data_sources: tuple[_DataSource, ...],
    ) -> dict[str, object]:
        metadata = self._parse_metadata(metadata_records, metadata_source)
        data_payloads: list[dict[str, object]] = []
        for data_source in data_sources:
            axis = self._parse_axis(
                data_source.records,
                data_source.source,
                data_source.detection,
            )
            vector_keys = tuple(
                vector_record.canonical_key
                for vector_record in self._index_vector_records(
                    data_source.records,
                    axis_length=len(axis.simulation_days),
                    source=data_source.source,
                )
            )
            data_payloads.append(
                {
                    "source": data_source.source,
                    "simulation_days": list(axis.simulation_days),
                    "report_steps": list(axis.report_steps),
                    "dates": [item.isoformat() for item in axis.dates],
                    "vector_keys": list(vector_keys),
                }
            )
        sources = tuple(
            source
            for source in (
                metadata_source,
                *(data_source.source for data_source in data_sources),
            )
            if source is not None
        )
        return {
            "metadata_source": metadata_source,
            "metadata": [
                {
                    "keyword": item.key.keyword,
                    "qualifier": item.key.qualifier,
                    "qualifier_kind": item.key.qualifier_kind,
                    "unit": item.unit,
                    "classification": item.classification,
                }
                for item in metadata.vectors
            ],
            "data_sources": data_payloads,
            "sources": list(sources),
            "unified": self._unified_flag(data_sources),
        }

    def _cache_key(
        self,
        metadata_path: str | Path,
        data_detections: tuple[FormatDetectionResult, ...],
    ) -> str:
        parts = [str(Path(metadata_path).resolve())]
        parts.extend(str(detection.path.resolve()) for detection in data_detections)
        return "|".join(parts)

    def _records_from_path(self, path: str | Path) -> tuple[TokenRecord, ...]:
        source_path = Path(path)
        try:
            data = source_path.read_bytes()
        except OSError as error:
            raise FileReadError(
                f"Could not read summary file {source_path}: {error}"
            ) from error
        text = self._decode_bytes(data)
        return self._split_records(tuple(self.parser.tokenizer.iter_tokens(text)))

    def _decode_bytes(self, data: bytes) -> str:
        if b"\x00" in data:
            raise ParseError(
                "Formatted summary reader received binary-looking data; "
                "binary summary decoding is not implemented"
            )
        try:
            return data.decode(self.encoding)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Could not decode formatted summary data as {self.encoding}"
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
            raise SummaryDataError(
                f"Unterminated summary keyword record starting with {current[0].text!r}"
            )
        if not records:
            raise SummaryDataError("Summary file contains no keyword records")
        return tuple(records)

    def _numeric_axis(
        self,
        record: TokenRecord,
        source: str | None,
    ) -> tuple[float, ...]:
        parsed = self.parser.parse_tokens(record, source=source)
        return tuple(
            self._required_number(parsed[0].values, index, parsed[0].name)
            for index in range(len(parsed[0].values))
        )

    def _integer_axis(
        self,
        record: TokenRecord,
        source: str | None,
    ) -> tuple[int, ...]:
        parsed = self.parser.parse_tokens(record, source=source)
        return tuple(
            self._required_integer(parsed[0].values, index, parsed[0].name)
            for index in range(len(parsed[0].values))
        )

    def _date_axis(
        self,
        record: TokenRecord,
        source: str | None,
    ) -> tuple[date, ...]:
        parsed = self.parser.parse_tokens(record, source=source)
        return tuple(
            self._required_date(parsed[0].values, index, parsed[0].name)
            for index in range(len(parsed[0].values))
        )

    def _first_record(
        self,
        records: tuple[TokenRecord, ...],
        name: str,
    ) -> TokenRecord | None:
        for record in records:
            if self._record_is(record, name):
                return record
        return None

    def _record_is(self, record: TokenRecord, name: str) -> bool:
        return bool(record) and record[0].text.strip().upper() == name

    def _required_string(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> str:
        if index >= len(values) or not isinstance(values[index], str):
            raise SummaryDataError(
                f"{keyword_name} value {index} must be a string"
            )
        return values[index]

    def _optional_string(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> str | None:
        if index >= len(values):
            return None
        return self._required_string(values, index, keyword_name)

    def _required_number(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> float:
        if index >= len(values):
            raise SummaryDataError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SummaryDataError(
                f"{keyword_name} value {index} must be numeric, got {value!r}"
            )
        return float(value)

    def _required_integer(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> int:
        if index >= len(values):
            raise SummaryDataError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, int):
            raise SummaryDataError(
                f"{keyword_name} value {index} must be an integer, got {value!r}"
            )
        return value

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
            raise SummaryDataError(
                f"{keyword_name} value {index} is not a valid ISO date: {raw_value!r}"
            ) from error

    def _unified_flag(self, data_sources: tuple[_DataSource, ...]) -> bool | None:
        flags = [
            data_source.detection.unified
            for data_source in data_sources
            if data_source.detection is not None
        ]
        if not flags:
            return None
        return all(flag is True for flag in flags)
