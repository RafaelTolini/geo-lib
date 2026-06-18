"""Restart dataset domain object."""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.restart.restart_report import RestartReport
from reservoir_data.exceptions.errors import InvalidReportStepError
from reservoir_data.schemas.queries import ReportStepMatchPolicy, ReportStepQuery


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

    def nearest_report_by_step(self, report_step: int) -> RestartReport:
        """Return the report with the nearest available report step."""

        if report_step < 0:
            raise ValueError("report_step must be non-negative")
        return self._nearest_report(
            target=float(report_step),
            value=lambda report: float(report.report_step),
            label="report step",
        )

    def nearest_report_by_simulation_days(
        self, simulation_days: float
    ) -> RestartReport:
        """Return the report nearest to a simulation day."""

        return self._nearest_report(
            target=float(simulation_days),
            value=lambda report: report.simulation_days,
            label="simulation day",
        )

    def nearest_report_by_date(self, report_date: date) -> RestartReport:
        """Return the report nearest to a report date."""

        return self._nearest_report(
            target=float(report_date.toordinal()),
            value=lambda report: (
                None
                if report.report_date is None
                else float(report.report_date.toordinal())
            ),
            label="report date",
        )

    def query(self, query: ReportStepQuery) -> RestartReport:
        """Return a report using a typed query."""

        nearest = query.match_policy is ReportStepMatchPolicy.NEAREST
        if query.report_step is not None:
            if nearest:
                return self.nearest_report_by_step(query.report_step)
            return self.report_by_step(query.report_step)
        if query.sequence_index is not None:
            return self.report_by_index(query.sequence_index)
        if query.simulation_days is not None:
            if nearest:
                return self.nearest_report_by_simulation_days(query.simulation_days)
            return self.report_by_simulation_days(query.simulation_days)
        if query.report_date is not None:
            if nearest:
                return self.nearest_report_by_date(query.report_date)
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

    def select_report_steps(self, report_steps: tuple[int, ...] | list[int]) -> "RestartDataset":
        """Return a dataset containing selected report steps in requested order."""

        selected = tuple(self.report_by_step(int(step)) for step in report_steps)
        return RestartDataset(
            reports=selected,
            sources=self.sources,
            unified=self.unified,
            grid=self.grid,
        )

    def timeline_rows(self) -> tuple[dict[str, object], ...]:
        """Return one metadata row per restart report."""

        return tuple(
            {
                "REPORT_STEP": report.report_step,
                "SEQUENCE_INDEX": report.header.sequence_index,
                "SIMULATION_DAYS": report.simulation_days,
                "DATE": (
                    None
                    if report.report_date is None
                    else report.report_date.isoformat()
                ),
                "SOURCE": report.header.source,
            }
            for report in self.reports
        )

    def to_csv(self, path: str | Path) -> None:
        """Write restart report metadata to CSV."""

        rows = self.timeline_rows()
        fieldnames = [
            "REPORT_STEP",
            "SEQUENCE_INDEX",
            "SIMULATION_DAYS",
            "DATE",
            "SOURCE",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _nearest_report(
        self,
        target: float,
        value: Callable[[RestartReport], float | None],
        label: str,
    ) -> RestartReport:
        candidates: list[tuple[float, int, RestartReport]] = []
        for index, report in enumerate(self.reports):
            candidate = value(report)
            if candidate is None:
                continue
            candidates.append((abs(candidate - target), index, report))
        if not candidates:
            raise InvalidReportStepError(
                f"No restart reports include {label} metadata"
            )
        return min(candidates, key=lambda item: (item[0], item[1]))[2]
