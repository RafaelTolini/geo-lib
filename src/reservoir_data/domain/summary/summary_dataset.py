"""Summary dataset domain object."""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.summary.summary_key import SummaryKey
from reservoir_data.domain.summary.summary_metadata import (
    SummaryMetadata,
    SummaryVectorMetadata,
)
from reservoir_data.domain.summary.summary_vector import SummaryVector
from reservoir_data.exceptions.errors import (
    InvalidReportStepError,
    MissingKeywordError,
    UnsupportedFormatError,
)


@dataclass(slots=True)
class SummaryDataset:
    """Summary metadata and lazily loaded vectors for one case."""

    metadata: SummaryMetadata
    simulation_days: tuple[float, ...]
    report_steps: tuple[int, ...]
    dates: tuple[date, ...]
    _vector_loaders: Mapping[str, Callable[[], SummaryVector]]
    sources: tuple[str, ...] = ()
    unified: bool | None = None
    _vector_cache: dict[str, SummaryVector] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "simulation_days",
            tuple(float(value) for value in self.simulation_days),
        )
        object.__setattr__(
            self,
            "report_steps",
            tuple(int(value) for value in self.report_steps),
        )
        object.__setattr__(self, "dates", tuple(self.dates))
        if not (
            len(self.simulation_days) == len(self.report_steps) == len(self.dates)
        ):
            raise InvalidReportStepError("Summary time axes have inconsistent lengths")
        object.__setattr__(self, "sources", tuple(self.sources))
        object.__setattr__(self, "_vector_loaders", dict(self._vector_loaders))

    def keys(self) -> tuple[str, ...]:
        """Return available vector keys."""

        return self.metadata.keys()

    def filter_keys(
        self,
        pattern: str = "*",
        keyword: str | None = None,
        qualifier: str | None = None,
        qualifier_kind: str | None = None,
    ) -> tuple[str, ...]:
        """Filter available vector keys."""

        return self.metadata.filter_keys(
            pattern=pattern,
            keyword=keyword,
            qualifier=qualifier,
            qualifier_kind=qualifier_kind,
        )

    def vector(self, key: str | SummaryKey) -> SummaryVector:
        """Return a summary vector, loading its values on demand."""

        metadata = self.metadata.vector_metadata(key)
        canonical = metadata.key.canonical
        if canonical not in self._vector_cache:
            loader = self._vector_loaders.get(canonical)
            if loader is None:
                raise MissingKeywordError(
                    f"Summary vector {canonical!r} has no data records"
                )
            self._vector_cache[canonical] = loader()
        return self._vector_cache[canonical]

    def is_vector_loaded(self, key: str | SummaryKey) -> bool:
        """Return whether a vector's values have already been loaded."""

        metadata = self.metadata.vector_metadata(key)
        return metadata.key.canonical in self._vector_cache

    def vectors(self, keys: Iterable[str] | None = None) -> tuple[SummaryVector, ...]:
        """Return selected vectors."""

        selected = self.keys() if keys is None else tuple(keys)
        return tuple(self.vector(key) for key in selected)

    def select(self, keys: Iterable[str]) -> "SummaryDataset":
        """Return a dataset exposing only selected vector keys."""

        selected_metadata: list[SummaryVectorMetadata] = []
        selected_loaders: dict[str, Callable[[], SummaryVector]] = {}
        selected_cache: dict[str, SummaryVector] = {}
        seen: set[str] = set()
        for key in keys:
            metadata = self.metadata.vector_metadata(key)
            canonical = metadata.key.canonical
            if canonical in seen:
                continue
            seen.add(canonical)
            selected_metadata.append(metadata)
            loader = self._vector_loaders.get(canonical)
            if loader is not None:
                selected_loaders[canonical] = loader
            if canonical in self._vector_cache:
                selected_cache[canonical] = self._vector_cache[canonical]

        dataset = SummaryDataset(
            metadata=SummaryMetadata(
                vectors=tuple(selected_metadata),
                source=self.metadata.source,
            ),
            simulation_days=self.simulation_days,
            report_steps=self.report_steps,
            dates=self.dates,
            _vector_loaders=selected_loaders,
            sources=self.sources,
            unified=self.unified,
        )
        dataset._vector_cache.update(selected_cache)
        return dataset

    def time_index_by_report_step(self, report_step: int) -> int:
        """Return the zero-based time-axis index for a report step."""

        for index, candidate in enumerate(self.report_steps):
            if candidate == report_step:
                return index
        raise InvalidReportStepError(f"Summary report step {report_step} was not found")

    def time_index_by_simulation_days(self, simulation_days: float) -> int:
        """Return the zero-based time-axis index for an exact simulation day."""

        target = float(simulation_days)
        for index, candidate in enumerate(self.simulation_days):
            if candidate == target:
                return index
        raise InvalidReportStepError(
            f"Summary simulation day {target} was not found"
        )

    def time_index_by_date(self, report_date: date) -> int:
        """Return the zero-based time-axis index for an exact report date."""

        for index, candidate in enumerate(self.dates):
            if candidate == report_date:
                return index
        raise InvalidReportStepError(f"Summary date {report_date} was not found")

    def to_numpy(self, keys: Iterable[str] | None = None) -> dict[str, object]:
        """Return selected vectors as NumPy arrays when NumPy is installed."""

        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError as error:
            raise UnsupportedFormatError("NumPy is not installed") from error
        selected = self.keys() if keys is None else tuple(keys)
        return {key: np.asarray(self.vector(key).values, dtype=float) for key in selected}

    def to_pandas(self, keys: Iterable[str] | None = None) -> object:
        """Return selected vectors as a pandas DataFrame when pandas is installed."""

        try:
            import pandas as pd  # type: ignore[import-not-found]
        except ImportError as error:
            raise UnsupportedFormatError("pandas is not installed") from error

        rows = self._rows(keys)
        return pd.DataFrame(rows)

    def to_csv(self, path: str | Path, keys: Iterable[str] | None = None) -> None:
        """Write selected vectors to CSV using the standard library."""

        rows = self._rows(keys)
        fieldnames = (
            ["DATE", "REPORT_STEP", "SIMULATION_DAYS"]
            if not rows
            else list(rows[0])
        )
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _rows(self, keys: Iterable[str] | None = None) -> list[dict[str, object]]:
        selected = self.keys() if keys is None else tuple(keys)
        vectors = tuple(self.vector(key) for key in selected)
        rows: list[dict[str, object]] = []
        for index, report_step in enumerate(self.report_steps):
            row: dict[str, object] = {
                "DATE": self.dates[index].isoformat(),
                "REPORT_STEP": report_step,
                "SIMULATION_DAYS": self.simulation_days[index],
            }
            for vector in vectors:
                row[vector.name] = vector.values[index]
            rows.append(row)
        return rows
