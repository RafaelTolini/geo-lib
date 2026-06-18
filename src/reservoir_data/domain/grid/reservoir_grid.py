"""Structured reservoir grid domain model."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.domain.grid.active_cell_map import ActiveCellMap
from reservoir_data.domain.grid.cell_index import CellIndex, CellIndexKind
from reservoir_data.domain.grid.grid_cell import GridCell
from reservoir_data.domain.grid.grid_dimensions import GridDimensions
from reservoir_data.domain.grid.grid_geometry import GridGeometry
from reservoir_data.domain.units import UnitSystem
from reservoir_data.exceptions.errors import InvalidCellIndexError, PropertyShapeError


@dataclass(frozen=True, slots=True)
class ReservoirGrid:
    """Structured reservoir grid with active/global index behavior."""

    dimensions: GridDimensions
    geometry: GridGeometry
    active_cell_map: ActiveCellMap
    unit_system: UnitSystem | str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "unit_system", UnitSystem.optional(self.unit_system))
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

    def cells(self) -> tuple[GridCell, ...]:
        """Return all cells in global index order."""

        return tuple(
            self.cell(CellIndex.global_cell(global_index))
            for global_index in range(self.total_cell_count)
        )

    def active_cells(self) -> tuple[GridCell, ...]:
        """Return active cells in active index order."""

        return tuple(
            self.cell(CellIndex.active_cell(active_index))
            for active_index in range(self.active_cell_count)
        )

    def inactive_cells(self) -> tuple[GridCell, ...]:
        """Return inactive cells in global index order."""

        return tuple(cell for cell in self.cells() if not cell.is_active)

    def cell_rows(self) -> tuple[dict[str, object], ...]:
        """Return lightweight cell metadata rows."""

        return tuple(
            {
                "GLOBAL_INDEX": cell.global_index,
                "ACTIVE_INDEX": cell.active_index,
                "I": cell.i,
                "J": cell.j,
                "K": cell.k,
                "SIMULATOR_I": cell.simulator_ijk[0],
                "SIMULATOR_J": cell.simulator_ijk[1],
                "SIMULATOR_K": cell.simulator_ijk[2],
                "ACTIVE": cell.is_active,
                "TOP": cell.top,
                "BOTTOM": cell.bottom,
                "DEPTH": cell.depth,
                "THICKNESS": cell.thickness,
            }
            for cell in self.cells()
        )
