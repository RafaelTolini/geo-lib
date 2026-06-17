"""Well timeline domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reservoir_data.domain.well.well_snapshot import WellSnapshot
from reservoir_data.exceptions.errors import InvalidReportStepError


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
