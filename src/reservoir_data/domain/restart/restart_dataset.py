"""Restart dataset domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.restart.restart_report import RestartReport
from reservoir_data.exceptions.errors import InvalidReportStepError
from reservoir_data.schemas.queries import ReportStepQuery


@dataclass(frozen=True, slots=True)
class RestartDataset:
    """Collection of restart reports for one case."""

    reports: tuple[RestartReport, ...]
    sources: tuple[str, ...] = ()
    unified: bool | None = None
    grid: ReservoirGrid | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "reports",
            tuple(sorted(self.reports, key=lambda report: report.header.sequence_index)),
        )
        object.__setattr__(self, "sources", tuple(self.sources))

    def __len__(self) -> int:
        return len(self.reports)

    def report_steps(self) -> tuple[int, ...]:
        """Return available report steps in sequence order."""

        return tuple(report.report_step for report in self.reports)

    def headers(self):
        """Return report headers in sequence order."""

        return tuple(report.header for report in self.reports)

    def report_by_step(self, report_step: int) -> RestartReport:
        """Return a report by exact report step."""

        for report in self.reports:
            if report.report_step == report_step:
                return report
        raise InvalidReportStepError(f"Report step {report_step} was not found")

    def report_by_index(self, sequence_index: int) -> RestartReport:
        """Return a report by zero-based sequence index."""

        if not 0 <= sequence_index < len(self.reports):
            raise InvalidReportStepError(
                f"Report sequence index {sequence_index} is outside available range"
            )
        return self.reports[sequence_index]

    def report_by_simulation_days(self, simulation_days: float) -> RestartReport:
        """Return a report by exact simulation day metadata."""

        for report in self.reports:
            if report.simulation_days == simulation_days:
                return report
        raise InvalidReportStepError(
            f"No report exists at simulation day {simulation_days}"
        )

    def report_by_date(self, report_date: date) -> RestartReport:
        """Return a report by exact report date metadata."""

        for report in self.reports:
            if report.report_date == report_date:
                return report
        raise InvalidReportStepError(f"No report exists at date {report_date}")

    def query(self, query: ReportStepQuery) -> RestartReport:
        """Return a report using a typed query."""

        if query.report_step is not None:
            return self.report_by_step(query.report_step)
        if query.sequence_index is not None:
            return self.report_by_index(query.sequence_index)
        if query.simulation_days is not None:
            return self.report_by_simulation_days(query.simulation_days)
        if query.report_date is not None:
            return self.report_by_date(query.report_date)
        raise InvalidReportStepError("ReportStepQuery does not specify a lookup field")

    def with_grid(self, grid: ReservoirGrid) -> "RestartDataset":
        """Return a dataset with reports associated with a grid."""

        return RestartDataset(
            reports=tuple(report.with_grid(grid) for report in self.reports),
            sources=self.sources,
            unified=self.unified,
            grid=grid,
        )
