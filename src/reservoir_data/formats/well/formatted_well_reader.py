"""Formatted restart well-data extractor."""

from __future__ import annotations

from dataclasses import dataclass, field

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_record import KeywordRecord, KeywordValue
from reservoir_data.domain.restart.restart_dataset import RestartDataset
from reservoir_data.domain.well.well_connection import WellConnection
from reservoir_data.domain.well.well_dataset import WellDataset
from reservoir_data.domain.well.well_segment import WellSegment
from reservoir_data.domain.well.well_snapshot import WellSnapshot
from reservoir_data.domain.well.well_timeline import WellTimeline
from reservoir_data.exceptions.errors import WellDataError


@dataclass(slots=True)
class _WorkingWell:
    name: str
    well_type: str
    is_open: bool
    connections: list[WellConnection] = field(default_factory=list)
    rates: dict[str, float] = field(default_factory=dict)
    segments: list[WellSegment] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class FormattedWellReader:
    """Extract scoped well records from formatted restart report payloads.

    Supported restart payload records:

    - `WELL 'PROD-1' 'PRODUCER' 'OPEN' /`
    - `WCONN 'PROD-1' 1 1 1 'OPEN' 'Z' 0.75 'MATRIX' /`
    - `WRATE 'PROD-1' 'OIL' 120.0 /`
    - `WSEG 'PROD-1' 1 0 1500.0 10.0 /`
    """

    def read(
        self,
        restarts: RestartDataset,
        load_segments: bool = True,
        grid: ReservoirGrid | None = None,
    ) -> WellDataset:
        """Build well timelines from supported restart report records."""

        snapshots_by_well: dict[str, list[WellSnapshot]] = {}
        for report in restarts.reports:
            working = self._working_wells_for_report(
                tuple(report.keywords),
                load_segments=load_segments,
                grid=grid or restarts.grid,
            )
            for well in working.values():
                snapshot = WellSnapshot(
                    well_name=well.name,
                    report_step=report.report_step,
                    simulation_days=report.simulation_days,
                    report_date=report.report_date,
                    well_type=well.well_type,
                    is_open=well.is_open,
                    connections=tuple(well.connections),
                    segments=tuple(well.segments),
                    rates=well.rates,
                )
                snapshots_by_well.setdefault(snapshot.well_name, []).append(snapshot)

        if not snapshots_by_well:
            raise WellDataError(
                "No supported WELL records were found in formatted restart reports"
            )

        timelines = tuple(
            WellTimeline(well_name=name, snapshots=tuple(snapshots))
            for name, snapshots in snapshots_by_well.items()
        )
        return WellDataset(timelines=timelines, sources=restarts.sources)

    def _working_wells_for_report(
        self,
        records: tuple[KeywordRecord, ...],
        load_segments: bool,
        grid: ReservoirGrid | None,
    ) -> dict[str, _WorkingWell]:
        working: dict[str, _WorkingWell] = {}
        for record in records:
            if record.name == "WELL":
                well = self._parse_well(record)
                working[well.name] = well
            elif record.name == "WCONN":
                name, connection = self._parse_connection(record, grid)
                self._require_working(working, name, record.name).connections.append(
                    connection
                )
            elif record.name == "WRATE":
                name, rate_name, value = self._parse_rate(record)
                self._require_working(working, name, record.name).rates[rate_name] = (
                    value
                )
            elif record.name == "WSEG" and load_segments:
                name, segment = self._parse_segment(record)
                self._require_working(working, name, record.name).segments.append(
                    segment
                )
        return working

    def _parse_well(self, record: KeywordRecord) -> _WorkingWell:
        values = record.values
        return _WorkingWell(
            name=self._required_string(values, 0, record.name).upper(),
            well_type=self._required_string(values, 1, record.name).upper(),
            is_open=self._status_to_open(
                self._required_string(values, 2, record.name),
                record.name,
            ),
        )

    def _parse_connection(
        self,
        record: KeywordRecord,
        grid: ReservoirGrid | None,
    ) -> tuple[str, WellConnection]:
        values = record.values
        name = self._required_string(values, 0, record.name).upper()
        cell = CellIndex.ijk(
            self._required_integer(values, 1, record.name),
            self._required_integer(values, 2, record.name),
            self._required_integer(values, 3, record.name),
            simulator_one_based=True,
        )
        if grid is not None:
            grid.global_index(cell)
        connection = WellConnection(
            cell=cell,
            is_open=self._status_to_open(
                self._required_string(values, 4, record.name),
                record.name,
            ),
            direction=self._optional_string(values, 5, record.name),
            connection_factor=self._optional_float(values, 6, record.name),
            classification=self._optional_string(values, 7, record.name),
        )
        return name, connection

    def _parse_rate(self, record: KeywordRecord) -> tuple[str, str, float]:
        values = record.values
        return (
            self._required_string(values, 0, record.name).upper(),
            self._required_string(values, 1, record.name).upper(),
            self._required_float(values, 2, record.name),
        )

    def _parse_segment(self, record: KeywordRecord) -> tuple[str, WellSegment]:
        values = record.values
        parent_id = self._required_integer(values, 2, record.name)
        try:
            segment = WellSegment(
                segment_id=self._required_integer(values, 1, record.name),
                parent_id=None if parent_id == 0 else parent_id,
                depth=self._optional_float(values, 3, record.name),
                length=self._optional_float(values, 4, record.name),
            )
        except ValueError as error:
            raise WellDataError(f"Invalid WSEG record: {error}") from error
        return self._required_string(values, 0, record.name).upper(), segment

    def _require_working(
        self,
        working: dict[str, _WorkingWell],
        name: str,
        record_name: str,
    ) -> _WorkingWell:
        try:
            return working[name]
        except KeyError as error:
            raise WellDataError(
                f"{record_name} record references well {name!r} before a WELL record"
            ) from error

    def _status_to_open(self, value: str, keyword_name: str) -> bool:
        normalized = value.strip().upper()
        if normalized in {"OPEN", "ON", "TRUE", "T"}:
            return True
        if normalized in {"SHUT", "SHUTIN", "CLOSED", "OFF", "FALSE", "F"}:
            return False
        raise WellDataError(
            f"{keyword_name} status must be OPEN or SHUT, got {value!r}"
        )

    def _required_string(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> str:
        if index >= len(values) or not isinstance(values[index], str):
            raise WellDataError(f"{keyword_name} value {index} must be a string")
        value = values[index].strip()
        if not value:
            raise WellDataError(f"{keyword_name} value {index} must not be empty")
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
            raise WellDataError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, int):
            raise WellDataError(
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
            raise WellDataError(f"{keyword_name} value {index} is missing")
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise WellDataError(
                f"{keyword_name} value {index} must be numeric, got {value!r}"
            )
        return float(value)

    def _optional_float(
        self,
        values: tuple[KeywordValue, ...],
        index: int,
        keyword_name: str,
    ) -> float | None:
        if index >= len(values):
            return None
        return self._required_float(values, index, keyword_name)
