"""Structured reservoir grid domain model."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.domain.grid.active_cell_map import ActiveCellMap
from reservoir_data.domain.grid.cell_index import CellIndex, CellIndexKind
from reservoir_data.domain.grid.grid_cell import GridCell
from reservoir_data.domain.grid.grid_dimensions import GridDimensions
from reservoir_data.domain.grid.grid_geometry import GridGeometry
from reservoir_data.exceptions.errors import InvalidCellIndexError, PropertyShapeError


@dataclass(frozen=True, slots=True)
class ReservoirGrid:
    """Structured reservoir grid with active/global index behavior."""

    dimensions: GridDimensions
    geometry: GridGeometry
    active_cell_map: ActiveCellMap

    def __post_init__(self) -> None:
        if self.geometry.dimensions != self.dimensions:
            raise ValueError("Grid geometry dimensions must match grid dimensions")
        if self.active_cell_map.total_cell_count != self.dimensions.total_cells:
            raise PropertyShapeError(
                f"Active cell map has {self.active_cell_map.total_cell_count} "
                f"cells; expected {self.dimensions.total_cells}"
            )

    @property
    def total_cell_count(self) -> int:
        """Number of global cells."""

        return self.dimensions.total_cells

    @property
    def active_cell_count(self) -> int:
        """Number of active cells."""

        return self.active_cell_map.active_cell_count

    def global_index(self, index: CellIndex) -> int:
        """Resolve any supported cell address to a global index."""

        if index.kind is CellIndexKind.IJK:
            i, j, k = index.zero_based_ijk()
            return self.dimensions.global_index(i, j, k)
        if index.kind is CellIndexKind.GLOBAL:
            if index.global_index is None:
                raise InvalidCellIndexError("Missing global index")
            self.dimensions.require_global_index(index.global_index)
            return index.global_index
        if index.active_index is None:
            raise InvalidCellIndexError("Missing active index")
        return self.active_cell_map.active_to_global_index(index.active_index)

    def ijk_from_global(self, global_index: int) -> tuple[int, int, int]:
        """Return zero-based IJK for a global index."""

        return self.dimensions.ijk_from_global(global_index)

    def active_index(self, index: CellIndex) -> int | None:
        """Resolve any supported cell address to an active index if active."""

        global_index = self.global_index(index)
        return self.active_cell_map.global_to_active_index(global_index)

    def is_active(self, index: CellIndex) -> bool:
        """Return whether a cell address resolves to an active cell."""

        global_index = self.global_index(index)
        return self.active_cell_map.is_active_global(global_index)

    def cell(self, index: CellIndex) -> GridCell:
        """Return a resolved grid cell."""

        global_index = self.global_index(index)
        return GridCell(
            grid=self,
            requested_index=index,
            global_index=global_index,
            active_index=self.active_cell_map.global_to_active_index(global_index),
            ijk=self.dimensions.ijk_from_global(global_index),
        )
