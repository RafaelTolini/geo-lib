"""Well connection domain object."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.domain.grid.cell_index import CellIndex


@dataclass(frozen=True, slots=True)
class WellConnection:
    """One well connection/completion in a grid cell."""

    cell: CellIndex
    is_open: bool
    direction: str | None = None
    connection_factor: float | None = None
    classification: str | None = None

    def __post_init__(self) -> None:
        if self.direction is not None:
            direction = self.direction.strip().upper()
            object.__setattr__(self, "direction", direction or None)
        if self.classification is not None:
            classification = self.classification.strip().upper()
            object.__setattr__(self, "classification", classification or None)
        if self.connection_factor is not None and self.connection_factor < 0:
            raise ValueError("connection_factor must be non-negative")
