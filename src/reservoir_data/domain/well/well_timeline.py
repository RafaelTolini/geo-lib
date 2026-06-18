"""Well timeline domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reservoir_data.domain.well.well_snapshot import WellSnapshot
from reservoir_data.exceptions.errors import InvalidReportStepError
from reservoir_data.schemas.queries import ReportStepMatchPolicy, ReportStepQuery


@dataclass(frozen=True, slots=True)
class WellTimeline:
    """Ordered snapshots for one well."""

    well_name: str
    snapshots: tuple[WellSnapshot, ...]

    def __post_init__(self) -> None:
        name = self.well_name.strip().upper()
        if not name:
            raise ValueError("well_name must not be empty")
        snapshots = tuple(
            sorted(self.snapshots, key=lambda snapshot: snapshot.report_step)
        )
        if any(snapshot.well_name != name for snapshot in snapshots):
            raise ValueError("All snapshots must belong to the timeline well")
        object.__setattr__(self, "well_name", name)
        object.__setattr__(self, "snapshots", snapshots)

    def report_steps(self) -> tuple[int, ...]:
        """Return available report steps."""

        return tuple(snapshot.report_step for snapshot in self.snapshots)

    def at_report_step(self, report_step: int) -> WellSnapshot:
        """Return the snapshot for an exact report step."""

        for snapshot in self.snapshots:
            if snapshot.report_step == report_step:
                return snapshot
        raise InvalidReportStepError(
            f"Well {self.well_name!r} has no report step {report_step}"
        )

    def at_simulation_days(self, simulation_days: float) -> WellSnapshot:
        """Return the snapshot for an exact simulation day."""

        for snapshot in self.snapshots:
            if snapshot.simulation_days == simulation_days:
                return snapshot
        raise InvalidReportStepError(
            f"Well {self.well_name!r} has no simulation day {simulation_days}"
        )

    def at_date(self, report_date: date) -> WellSnapshot:
        """Return the snapshot for an exact report date."""

        for snapshot in self.snapshots:
            if snapshot.report_date == report_date:
                return snapshot
        raise InvalidReportStepError(
            f"Well {self.well_name!r} has no report date {report_date}"
        )

    def nearest_at_report_step(self, report_step: int) -> WellSnapshot:
        """Return the snapshot with the nearest available report step."""

        if report_step < 0:
            raise ValueError("report_step must be non-negative")
        return self._nearest_snapshot(
            target=float(report_step),
            value=lambda snapshot: float(snapshot.report_step),
            label="report step",
        )

    def nearest_at_simulation_days(self, simulation_days: float) -> WellSnapshot:
        """Return the snapshot nearest to a simulation day."""

        return self._nearest_snapshot(
            target=float(simulation_days),
            value=lambda snapshot: snapshot.simulation_days,
            label="simulation day",
        )

    def nearest_at_date(self, report_date: date) -> WellSnapshot:
        """Return the snapshot nearest to a report date."""

        return self._nearest_snapshot(
            target=float(report_date.toordinal()),
            value=lambda snapshot: (
                None
                if snapshot.report_date is None
                else float(snapshot.report_date.toordinal())
            ),
            label="report date",
        )

    def query(self, query: ReportStepQuery) -> WellSnapshot:
        """Return a snapshot using a typed report query."""

        nearest = query.match_policy is ReportStepMatchPolicy.NEAREST
        if query.report_step is not None:
            if nearest:
                return self.nearest_at_report_step(query.report_step)
            return self.at_report_step(query.report_step)
        if query.sequence_index is not None:
            if not 0 <= query.sequence_index < len(self.snapshots):
                raise InvalidReportStepError(
                    f"Well {self.well_name!r} sequence index "
                    f"{query.sequence_index} is outside available range"
                )
            return self.snapshots[query.sequence_index]
        if query.simulation_days is not None:
            if nearest:
                return self.nearest_at_simulation_days(query.simulation_days)
            return self.at_simulation_days(query.simulation_days)
        if query.report_date is not None:
            if nearest:
                return self.nearest_at_date(query.report_date)
            return self.at_date(query.report_date)
        raise InvalidReportStepError("ReportStepQuery does not specify a lookup field")

    def _nearest_snapshot(
        self,
        target: float,
        value,
        label: str,
    ) -> WellSnapshot:
        candidates: list[tuple[float, int, WellSnapshot]] = []
        for index, snapshot in enumerate(self.snapshots):
            candidate = value(snapshot)
            if candidate is None:
                continue
            candidates.append((abs(candidate - target), index, snapshot))
        if not candidates:
            raise InvalidReportStepError(
                f"Well {self.well_name!r} has no {label} metadata"
            )
        return min(candidates, key=lambda item: (item[0], item[1]))[2]
