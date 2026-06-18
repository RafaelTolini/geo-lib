"""Grid cell view."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.exceptions.errors import GridGeometryError

if TYPE_CHECKING:
    from reservoir_data.domain.property.grid_property import GridProperty
    from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid


@dataclass(frozen=True, slots=True)
class GridCell:
    """One resolved cell in a reservoir grid."""

    grid: "ReservoirGrid"
    requested_index: CellIndex
    global_index: int
    active_index: int | None
    ijk: tuple[int, int, int]

    @property
    def i(self) -> int:
        """Zero-based I index."""

        return self.ijk[0]

    @property
    def j(self) -> int:
        """Zero-based J index."""

        return self.ijk[1]

    @property
    def k(self) -> int:
        """Zero-based K index."""

        return self.ijk[2]

    @property
    def simulator_ijk(self) -> tuple[int, int, int]:
        """One-based simulator IJK index."""

        return self.i + 1, self.j + 1, self.k + 1

    @property
    def is_active(self) -> bool:
        """Return whether the cell is active."""

        return self.active_index is not None

    @property
    def depth(self) -> float:
        """Depth derived from stored ZCORN values."""

        return self.grid.geometry.cell_depth(self.global_index)

    @property
    def top(self) -> float:
        """Top depth derived from stored ZCORN values."""

        return self.grid.geometry.cell_top(self.global_index)

    @property
    def bottom(self) -> float:
        """Bottom depth derived from stored ZCORN values."""

        return self.grid.geometry.cell_bottom(self.global_index)

    @property
    def thickness(self) -> float:
        """Thickness derived from stored ZCORN values."""

        return self.grid.geometry.cell_thickness(self.global_index)

    @property
    def corner_depths(self) -> tuple[float, ...]:
        """Return the eight stored ZCORN depths for this cell."""

        return self.grid.geometry.cell_corner_depths(self.global_index)

    @property
    def center(self) -> tuple[float, float, float]:
        """Return a logical IJK center with depth from geometry."""

        return self.i + 0.5, self.j + 0.5, self.depth

    def property_value(self, property_: "GridProperty") -> KeywordValue:
        """Return a compatible grid property's value at this cell."""

        return property_.value_at(CellIndex.global_cell(self.global_index))

    @property
    def volume(self) -> float:
        """Cell volume is not available in the minimal M3 geometry model."""

        raise GridGeometryError(
            "Cell volume calculation requires full corner-point geometry support"
        )
