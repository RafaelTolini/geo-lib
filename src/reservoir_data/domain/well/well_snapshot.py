"""Well snapshot domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping

from reservoir_data.domain.well.well_connection import WellConnection
from reservoir_data.domain.well.well_segment import WellSegment
from reservoir_data.exceptions.errors import WellDataError


@dataclass(frozen=True, slots=True)
class WellSnapshot:
    """State for one well at one report step."""

    well_name: str
    report_step: int
    well_type: str
    is_open: bool
    simulation_days: float | None = None
    report_date: date | None = None
    connections: tuple[WellConnection, ...] = ()
    segments: tuple[WellSegment, ...] = ()
    rates: Mapping[str, float] = MappingProxyType({})

    def __post_init__(self) -> None:
        name = self.well_name.strip().upper()
        if not name:
            raise ValueError("well_name must not be empty")
        object.__setattr__(self, "well_name", name)

        well_type = self.well_type.strip().upper()
        if not well_type:
            raise ValueError("well_type must not be empty")
        object.__setattr__(self, "well_type", well_type)

        if self.report_step < 0:
            raise ValueError("report_step must be non-negative")
        object.__setattr__(self, "connections", tuple(self.connections))
        object.__setattr__(self, "segments", tuple(self.segments))
        object.__setattr__(
            self,
            "rates",
            MappingProxyType(
                {key.strip().upper(): float(value) for key, value in self.rates.items()}
            ),
        )

    def rate(self, name: str) -> float:
        """Return one named rate."""

        normalized = name.strip().upper()
        try:
            return self.rates[normalized]
        except KeyError as error:
            raise WellDataError(
                f"Well {self.well_name!r} has no rate {normalized!r} at "
                f"report step {self.report_step}"
            ) from error
