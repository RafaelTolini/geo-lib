"""RFT/PLT record domain object."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from reservoir_data.domain.rft.rft_cell_measurement import RftCellMeasurement


@dataclass(slots=True)
class RftRecord:
    """One RFT/PLT measurement record for a well and date."""

    well_name: str
    report_date: date
    record_type: str
    _measurement_loader: Callable[[], tuple[RftCellMeasurement, ...]]
    source: str | None = None
    _measurements: tuple[RftCellMeasurement, ...] | None = field(
        default=None,
        init=False,
    )

    def __post_init__(self) -> None:
        name = self.well_name.strip().upper()
        if not name:
            raise ValueError("well_name must not be empty")
        object.__setattr__(self, "well_name", name)

        record_type = self.record_type.strip().upper()
        if not record_type:
            raise ValueError("record_type must not be empty")
        object.__setattr__(self, "record_type", record_type)

    @property
    def measurements(self) -> tuple[RftCellMeasurement, ...]:
        """Return lazily loaded cell measurements."""

        if self._measurements is None:
            self._measurements = self._measurement_loader()
        return self._measurements

    @property
    def is_measurements_loaded(self) -> bool:
        """Return whether measurements have already been loaded."""

        return self._measurements is not None
