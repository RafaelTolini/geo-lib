"""Restart report step domain object."""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.domain.restart.restart_header import RestartHeader
from reservoir_data.exceptions.errors import MissingKeywordError


@dataclass(slots=True)
class RestartReport:
    """One restart report with lazily loaded keyword payload."""

    header: RestartHeader
    _keyword_loader: Callable[[], KeywordDataset]
    grid: ReservoirGrid | None = None
    _keyword_dataset: KeywordDataset | None = field(default=None, init=False)

    @property
    def report_step(self) -> int:
        """Report step number."""

        return self.header.report_step

    @property
    def simulation_days(self) -> float | None:
        """Simulation day metadata when available."""

        return self.header.simulation_days

    @property
    def report_date(self) -> date | None:
        """Report date metadata when available."""

        return self.header.report_date

    @property
    def is_payload_loaded(self) -> bool:
        """Return whether the keyword payload has been loaded."""

        return self._keyword_dataset is not None

    @property
    def keywords(self) -> KeywordDataset:
        """Return the lazily loaded report keyword dataset."""

        if self._keyword_dataset is None:
            self._keyword_dataset = self._keyword_loader()
        return self._keyword_dataset

    def property(
        self, name: str, grid: ReservoirGrid | None = None
    ) -> GridProperty:
        """Return a grid property from a report keyword."""

        record = self.keywords.record(name)
        if record is None:
            raise MissingKeywordError(f"Restart property {name!r} was not found")
        return GridProperty.from_record(record, grid=grid or self.grid)

    def keyword_names(self) -> tuple[str, ...]:
        """Return restart keyword names for this report."""

        return self.keywords.names()

    def has_keyword(self, name: str) -> bool:
        """Return whether this report contains a keyword."""

        return self.keywords.has_keyword(name)

    def properties(
        self,
        names: tuple[str, ...] | list[str] | None = None,
        grid: ReservoirGrid | None = None,
    ) -> PropertyCollection:
        """Return selected restart keywords as a property collection."""

        selected_names = self.keyword_names() if names is None else tuple(names)
        return PropertyCollection(
            properties=tuple(
                self.property(name, grid=grid or self.grid)
                for name in selected_names
            ),
            source=self.header.source,
        )

    def keyword_rows(self) -> tuple[dict[str, object], ...]:
        """Return metadata rows for report payload keywords."""

        return tuple(
            {
                "REPORT_STEP": self.report_step,
                "SEQUENCE_INDEX": self.header.sequence_index,
                "KEYWORD": record.name,
                "OCCURRENCE_INDEX": occurrence_index,
                "TYPE": record.keyword_type.value,
                "VALUE_COUNT": record.element_count,
                "SOURCE": record.source or self.header.source,
            }
            for occurrence_index, record in enumerate(self.keywords.records)
        )

    def keywords_to_csv(self, path: str | Path) -> None:
        """Write report payload keyword metadata rows to CSV."""

        fieldnames = [
            "REPORT_STEP",
            "SEQUENCE_INDEX",
            "KEYWORD",
            "OCCURRENCE_INDEX",
            "TYPE",
            "VALUE_COUNT",
            "SOURCE",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.keyword_rows())

    def with_grid(self, grid: ReservoirGrid) -> "RestartReport":
        """Return a report using the same lazy payload and a grid association."""

        report = RestartReport(
            header=self.header,
            _keyword_loader=self._keyword_loader,
            grid=grid,
        )
        report._keyword_dataset = self._keyword_dataset
        return report

    def with_header(self, header: RestartHeader) -> "RestartReport":
        """Return a report using the same payload and a different header."""

        report = RestartReport(
            header=header,
            _keyword_loader=self._keyword_loader,
            grid=self.grid,
        )
        report._keyword_dataset = self._keyword_dataset
        return report
