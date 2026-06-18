"""RFT/PLT record domain object."""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

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

    def measurement_rows(self) -> tuple[dict[str, object], ...]:
        """Return flattened measurement rows for this record."""

        rows: list[dict[str, object]] = []
        for measurement_index, measurement in enumerate(self.measurements):
            i, j, k = measurement.cell.zero_based_ijk()
            row: dict[str, object] = {
                "WELL": self.well_name,
                "DATE": self.report_date.isoformat(),
                "TYPE": self.record_type,
                "MEASUREMENT_INDEX": measurement_index,
                "I": i,
                "J": j,
                "K": k,
                "SIMULATOR_I": i + 1,
                "SIMULATOR_J": j + 1,
                "SIMULATOR_K": k + 1,
                "DEPTH": measurement.depth,
                "PRESSURE": measurement.pressure,
            }
            for phase, value in measurement.saturations.items():
                row[f"SATURATION_{phase}"] = value
            for phase, value in measurement.rates.items():
                row[f"RATE_{phase}"] = value
            rows.append(row)
        return tuple(rows)

    def measurements_to_csv(self, path: str | Path) -> None:
        """Write flattened measurement rows for this record to CSV."""

        _write_measurement_rows(path, self.measurement_rows())


def _measurement_fieldnames(rows: tuple[dict[str, object], ...]) -> list[str]:
    base = [
        "WELL",
        "DATE",
        "TYPE",
        "MEASUREMENT_INDEX",
        "I",
        "J",
        "K",
        "SIMULATOR_I",
        "SIMULATOR_J",
        "SIMULATOR_K",
        "DEPTH",
        "PRESSURE",
    ]
    dynamic = sorted(
        key
        for row in rows
        for key in row
        if key.startswith("SATURATION_") or key.startswith("RATE_")
    )
    return [*base, *dict.fromkeys(dynamic)]


def _write_measurement_rows(
    path: str | Path,
    rows: tuple[dict[str, object], ...],
) -> None:
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=_measurement_fieldnames(rows))
        writer.writeheader()
        writer.writerows(rows)
