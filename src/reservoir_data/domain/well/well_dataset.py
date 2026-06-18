"""Well dataset domain object."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

from reservoir_data.domain.well.well_timeline import WellTimeline
from reservoir_data.exceptions.errors import WellDataError


@dataclass(frozen=True, slots=True)
class WellDataset:
    """Collection of well timelines for one case."""

    timelines: tuple[WellTimeline, ...]
    sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        timelines = tuple(sorted(self.timelines, key=lambda item: item.well_name))
        names = [timeline.well_name for timeline in timelines]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise WellDataError(f"Duplicate well timelines: {duplicate_list}")
        object.__setattr__(self, "timelines", timelines)
        object.__setattr__(self, "sources", tuple(self.sources))

    def names(self) -> tuple[str, ...]:
        """Return well names."""

        return tuple(timeline.well_name for timeline in self.timelines)

    def has_well(self, well_name: str) -> bool:
        """Return whether a well timeline exists."""

        normalized = well_name.strip().upper()
        return normalized in self.names()

    def filter_names(self, pattern: str = "*") -> tuple[str, ...]:
        """Return well names matching a case-insensitive wildcard pattern."""

        normalized_pattern = pattern.strip().upper() or "*"
        return tuple(
            name for name in self.names() if fnmatchcase(name, normalized_pattern)
        )

    def select(self, well_names: tuple[str, ...] | list[str]) -> "WellDataset":
        """Return a dataset containing selected well timelines."""

        selected = tuple(self.timeline(name) for name in well_names)
        return WellDataset(timelines=selected, sources=self.sources)

    def timeline(self, well_name: str) -> WellTimeline:
        """Return one well timeline."""

        normalized = well_name.strip().upper()
        for timeline in self.timelines:
            if timeline.well_name == normalized:
                return timeline
        raise WellDataError(f"Well {normalized!r} was not found")

    def rows(self) -> tuple[dict[str, object], ...]:
        """Return flattened well snapshot rows."""

        rows: list[dict[str, object]] = []
        for timeline in self.timelines:
            for snapshot in timeline.snapshots:
                row: dict[str, object] = {
                    "WELL": snapshot.well_name,
                    "REPORT_STEP": snapshot.report_step,
                    "SIMULATION_DAYS": snapshot.simulation_days,
                    "DATE": (
                        None
                        if snapshot.report_date is None
                        else snapshot.report_date.isoformat()
                    ),
                    "WELL_TYPE": snapshot.well_type,
                    "OPEN": snapshot.is_open,
                    "CONNECTION_COUNT": len(snapshot.connections),
                    "SEGMENT_COUNT": len(snapshot.segments),
                }
                for name, value in snapshot.rates.items():
                    row[f"RATE_{name}"] = value
                rows.append(row)
        return tuple(rows)

    def to_csv(self, path: str | Path) -> None:
        """Write flattened well snapshot rows to CSV."""

        rows = self.rows()
        base_fieldnames = [
            "WELL",
            "REPORT_STEP",
            "SIMULATION_DAYS",
            "DATE",
            "WELL_TYPE",
            "OPEN",
            "CONNECTION_COUNT",
            "SEGMENT_COUNT",
        ]
        rate_fieldnames = sorted(
            key
            for row in rows
            for key in row
            if key.startswith("RATE_")
        )
        fieldnames = [*base_fieldnames, *dict.fromkeys(rate_fieldnames)]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def connection_rows(self) -> tuple[dict[str, object], ...]:
        """Return flattened well connection rows."""

        rows: list[dict[str, object]] = []
        for timeline in self.timelines:
            for snapshot in timeline.snapshots:
                for connection_index, connection in enumerate(snapshot.connections):
                    i, j, k = connection.cell.zero_based_ijk()
                    row: dict[str, object] = {
                        "WELL": snapshot.well_name,
                        "REPORT_STEP": snapshot.report_step,
                        "SIMULATION_DAYS": snapshot.simulation_days,
                        "DATE": (
                            None
                            if snapshot.report_date is None
                            else snapshot.report_date.isoformat()
                        ),
                        "CONNECTION_INDEX": connection_index,
                        "I": i,
                        "J": j,
                        "K": k,
                        "SIMULATOR_I": i + 1,
                        "SIMULATOR_J": j + 1,
                        "SIMULATOR_K": k + 1,
                        "OPEN": connection.is_open,
                        "DIRECTION": connection.direction,
                        "CONNECTION_FACTOR": connection.connection_factor,
                        "CLASSIFICATION": connection.classification,
                    }
                    rows.append(row)
        return tuple(rows)

    def segment_rows(self) -> tuple[dict[str, object], ...]:
        """Return flattened well segment rows."""

        rows: list[dict[str, object]] = []
        for timeline in self.timelines:
            for snapshot in timeline.snapshots:
                for segment in snapshot.segments:
                    rows.append(
                        {
                            "WELL": snapshot.well_name,
                            "REPORT_STEP": snapshot.report_step,
                            "SIMULATION_DAYS": snapshot.simulation_days,
                            "DATE": (
                                None
                                if snapshot.report_date is None
                                else snapshot.report_date.isoformat()
                            ),
                            "SEGMENT_ID": segment.segment_id,
                            "PARENT_ID": segment.parent_id,
                            "DEPTH": segment.depth,
                            "LENGTH": segment.length,
                        }
                    )
        return tuple(rows)

    def connections_to_csv(self, path: str | Path) -> None:
        """Write flattened well connection rows to CSV."""

        fieldnames = [
            "WELL",
            "REPORT_STEP",
            "SIMULATION_DAYS",
            "DATE",
            "CONNECTION_INDEX",
            "I",
            "J",
            "K",
            "SIMULATOR_I",
            "SIMULATOR_J",
            "SIMULATOR_K",
            "OPEN",
            "DIRECTION",
            "CONNECTION_FACTOR",
            "CLASSIFICATION",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.connection_rows())

    def segments_to_csv(self, path: str | Path) -> None:
        """Write flattened well segment rows to CSV."""

        fieldnames = [
            "WELL",
            "REPORT_STEP",
            "SIMULATION_DAYS",
            "DATE",
            "SEGMENT_ID",
            "PARENT_ID",
            "DEPTH",
            "LENGTH",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.segment_rows())
