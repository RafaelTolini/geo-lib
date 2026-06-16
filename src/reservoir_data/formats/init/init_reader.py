"""Minimal INIT/property reader."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.exceptions.errors import MissingKeywordError
from reservoir_data.formats.common.formatted_keyword_reader import FormattedKeywordReader


@dataclass(frozen=True, slots=True)
class InitReader:
    """Read minimal formatted INIT/property keyword files."""

    keyword_reader: FormattedKeywordReader = field(
        default_factory=FormattedKeywordReader
    )

    def read(
        self,
        path: str | Path,
        grid: ReservoirGrid | None = None,
        names: Sequence[str] | None = None,
    ) -> PropertyCollection:
        """Read properties from a formatted INIT file."""

        dataset = self.keyword_reader.read(path)
        return self.from_dataset(dataset, grid=grid, names=names)

    def from_dataset(
        self,
        dataset: KeywordDataset,
        grid: ReservoirGrid | None = None,
        names: Sequence[str] | None = None,
    ) -> PropertyCollection:
        """Build a property collection from a parsed keyword dataset."""

        records = []
        if names is None:
            records = list(dataset.records)
        else:
            for name in names:
                record = dataset.record(name)
                if record is None:
                    raise MissingKeywordError(f"Property {name!r} was not found")
                records.append(record)

        properties = tuple(
            GridProperty.from_record(record, grid=grid) for record in records
        )
        return PropertyCollection(properties=properties, source=dataset.source)
