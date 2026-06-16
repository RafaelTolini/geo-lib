"""Grid geometry arrays and lightweight geometry queries."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from reservoir_data.domain.grid.grid_dimensions import GridDimensions
from reservoir_data.exceptions.errors import GridGeometryError


@dataclass(frozen=True, slots=True)
class GridGeometry:
    """Validated GRDECL-compatible geometry arrays.

    This milestone stores coordinate and ZCORN payloads and exposes lightweight
    depth-derived values. Full corner-point coordinate reconstruction and volume
    calculations are intentionally left for later geometry reader milestones.
    """

    dimensions: GridDimensions
    coord: tuple[float, ...]
    zcorn: tuple[float, ...]
    map_axes: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        coord = tuple(float(value) for value in self.coord)
        zcorn = tuple(float(value) for value in self.zcorn)
        map_axes = None
        if self.map_axes is not None:
            map_axes = tuple(float(value) for value in self.map_axes)

        expected_coord = 6 * self.dimensions.pillar_count
        expected_zcorn = 8 * self.dimensions.total_cells
        if len(coord) != expected_coord:
            raise GridGeometryError(
                f"COORD has {len(coord)} values; expected {expected_coord}"
            )
        if len(zcorn) != expected_zcorn:
            raise GridGeometryError(
                f"ZCORN has {len(zcorn)} values; expected {expected_zcorn}"
            )
        if map_axes is not None and len(map_axes) != 6:
            raise GridGeometryError("MAPAXES must contain exactly 6 values")

        object.__setattr__(self, "coord", coord)
        object.__setattr__(self, "zcorn", zcorn)
        object.__setattr__(self, "map_axes", map_axes)

    @classmethod
    def from_sequences(
        cls,
        dimensions: GridDimensions,
        coord: Sequence[int | float],
        zcorn: Sequence[int | float],
        map_axes: Sequence[int | float] | None = None,
    ) -> "GridGeometry":
        """Build geometry from numeric sequences."""

        return cls(
            dimensions=dimensions,
            coord=tuple(float(value) for value in coord),
            zcorn=tuple(float(value) for value in zcorn),
            map_axes=None if map_axes is None else tuple(float(value) for value in map_axes),
        )

    def cell_corner_depths(self, global_index: int) -> tuple[float, ...]:
        """Return the eight stored ZCORN depths for a global cell."""

        self.dimensions.require_global_index(global_index)
        start = 8 * global_index
        return self.zcorn[start : start + 8]

    def cell_top(self, global_index: int) -> float:
        """Return the mean top depth from the first four stored corners."""

        corners = self.cell_corner_depths(global_index)
        return sum(corners[:4]) / 4.0

    def cell_bottom(self, global_index: int) -> float:
        """Return the mean bottom depth from the last four stored corners."""

        corners = self.cell_corner_depths(global_index)
        return sum(corners[4:]) / 4.0

    def cell_depth(self, global_index: int) -> float:
        """Return the mean depth from all stored cell ZCORN values."""

        corners = self.cell_corner_depths(global_index)
        return sum(corners) / 8.0

    def cell_thickness(self, global_index: int) -> float:
        """Return absolute bottom-top depth difference."""

        return abs(self.cell_bottom(global_index) - self.cell_top(global_index))

    def export_coord(self) -> tuple[float, ...]:
        """Return GRDECL-compatible COORD values."""

        return tuple(self.coord)

    def export_zcorn(self) -> tuple[float, ...]:
        """Return GRDECL-compatible ZCORN values."""

        return tuple(self.zcorn)
