"""Structured grid dimensions."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.exceptions.errors import InvalidCellIndexError


@dataclass(frozen=True, slots=True)
class GridDimensions:
    """Structured grid dimensions using zero-based Python indexing."""

    nx: int
    ny: int
    nz: int

    def __post_init__(self) -> None:
        for name, value in (("nx", self.nx), ("ny", self.ny), ("nz", self.nz)):
            if value <= 0:
                raise ValueError(f"{name} must be positive")

    @property
    def total_cells(self) -> int:
        """Total number of global cells."""

        return self.nx * self.ny * self.nz

    @property
    def pillar_count(self) -> int:
        """Number of corner-point coordinate pillars."""

        return (self.nx + 1) * (self.ny + 1)

    def contains_ijk(self, i: int, j: int, k: int) -> bool:
        """Return whether a zero-based IJK address is inside the grid."""

        return 0 <= i < self.nx and 0 <= j < self.ny and 0 <= k < self.nz

    def require_ijk(self, i: int, j: int, k: int) -> None:
        """Raise if a zero-based IJK address is outside the grid."""

        if not self.contains_ijk(i, j, k):
            raise InvalidCellIndexError(
                f"Cell index (i={i}, j={j}, k={k}) is outside dimensions "
                f"({self.nx}, {self.ny}, {self.nz})"
            )

    def require_global_index(self, global_index: int) -> None:
        """Raise if a global index is outside the grid."""

        if not 0 <= global_index < self.total_cells:
            raise InvalidCellIndexError(
                f"Global cell index {global_index} is outside 0.."
                f"{self.total_cells - 1}"
            )

    def global_index(self, i: int, j: int, k: int) -> int:
        """Return the zero-based global index for a zero-based IJK address."""

        self.require_ijk(i, j, k)
        return i + self.nx * (j + self.ny * k)

    def ijk_from_global(self, global_index: int) -> tuple[int, int, int]:
        """Return zero-based IJK for a zero-based global index."""

        self.require_global_index(global_index)
        cells_per_layer = self.nx * self.ny
        k, within_layer = divmod(global_index, cells_per_layer)
        j, i = divmod(within_layer, self.nx)
        return i, j, k
