"""Minimal GRID/EGRID reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.formats.common.formatted_keyword_reader import FormattedKeywordReader
from reservoir_data.formats.grdecl.grid_builder import GrdeclGridBuilder


@dataclass(frozen=True, slots=True)
class GridReader:
    """Read minimal formatted GRID/EGRID keyword files.

    This reader supports formatted GRDECL-style keyword content containing
    `SPECGRID`, `COORD`, `ZCORN`, and optional `ACTNUM`. It does not decode
    simulator-specific unformatted binary GRID/EGRID keyword payloads.
    """

    keyword_reader: FormattedKeywordReader = field(
        default_factory=FormattedKeywordReader
    )
    grid_builder: GrdeclGridBuilder = field(default_factory=GrdeclGridBuilder)

    def read(self, path: str | Path) -> ReservoirGrid:
        """Read a minimal formatted grid file."""

        dataset = self.keyword_reader.read(path)
        return self.from_dataset(dataset)

    def from_dataset(self, dataset: KeywordDataset) -> ReservoirGrid:
        """Build a grid from a parsed keyword dataset."""

        return self.grid_builder.build(dataset)
