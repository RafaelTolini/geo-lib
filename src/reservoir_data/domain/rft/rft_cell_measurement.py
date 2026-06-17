"""RFT/PLT cell measurement domain object."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from reservoir_data.domain.grid.cell_index import CellIndex


@dataclass(frozen=True, slots=True)
class RftCellMeasurement:
    """One measured cell in an RFT/PLT record."""

    cell: CellIndex
    depth: float | None = None
    pressure: float | None = None
    saturations: Mapping[str, float] = MappingProxyType({})
    rates: Mapping[str, float] = MappingProxyType({})

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "saturations",
            MappingProxyType(
                {
                    key.strip().upper(): float(value)
                    for key, value in self.saturations.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "rates",
            MappingProxyType(
                {key.strip().upper(): float(value) for key, value in self.rates.items()}
            ),
        )
