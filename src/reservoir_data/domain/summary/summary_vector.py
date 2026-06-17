"""Summary time-series vector domain object."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from reservoir_data.domain.summary.summary_key import SummaryKey
from reservoir_data.exceptions.errors import (
    InvalidReportStepError,
    SummaryDataError,
    UnsupportedFormatError,
)


@dataclass(frozen=True, slots=True)
class SummaryVector:
    """One numeric summary vector over the case time axis."""

    key: SummaryKey
    values: tuple[float, ...]
    simulation_days: tuple[float, ...]
    report_steps: tuple[int, ...]
    dates: tuple[date, ...]
    unit: str | None = None

    def __post_init__(self) -> None:
        values = tuple(float(value) for value in self.values)
        simulation_days = tuple(float(value) for value in self.simulation_days)
        report_steps = tuple(int(value) for value in self.report_steps)
        dates = tuple(self.dates)
        size = len(values)
        if not (
            len(simulation_days) == size
            and len(report_steps) == size
            and len(dates) == size
        ):
            raise SummaryDataError(
                f"Summary vector {self.key.canonical!r} has inconsistent axis lengths"
            )
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "simulation_days", simulation_days)
        object.__setattr__(self, "report_steps", report_steps)
        object.__setattr__(self, "dates", dates)

    @property
    def name(self) -> str:
        """Return the canonical public vector key."""

        return self.key.canonical

    def first_value(self) -> float:
        """Return the first vector value."""

        return self._value_at_offset(0)

    def last_value(self) -> float:
        """Return the last vector value."""

        return self._value_at_offset(len(self.values) - 1)

    def value_at_report_step(self, report_step: int) -> float:
        """Return the value at an exact report step."""

        for index, candidate in enumerate(self.report_steps):
            if candidate == report_step:
                return self.values[index]
        raise InvalidReportStepError(
            f"Summary vector {self.name!r} has no report step {report_step}"
        )

    def interpolate_at(self, simulation_day: float) -> float:
        """Linearly interpolate a value by simulation day.

        This is a generic numeric interpolation rule for the scoped formatted
        summary slice. Simulator-specific rate/cumulative resampling rules
        remain deferred until independently verified.
        """

        if not self.values:
            raise SummaryDataError(f"Summary vector {self.name!r} contains no values")

        target = float(simulation_day)
        days = self.simulation_days
        if target < days[0] or target > days[-1]:
            raise InvalidReportStepError(
                f"Simulation day {target} is outside vector {self.name!r}"
            )
        for index, day in enumerate(days):
            if day == target:
                return self.values[index]
        for right_index in range(1, len(days)):
            left_day = days[right_index - 1]
            right_day = days[right_index]
            if left_day <= target <= right_day:
                fraction = (target - left_day) / (right_day - left_day)
                left_value = self.values[right_index - 1]
                right_value = self.values[right_index]
                return left_value + fraction * (right_value - left_value)
        raise InvalidReportStepError(
            f"Simulation day {target} is outside vector {self.name!r}"
        )

    def resample(self, interval_days: float) -> "SummaryVector":
        """Return a linearly resampled vector at a fixed day interval."""

        interval = float(interval_days)
        if interval <= 0:
            raise ValueError("interval_days must be positive")
        if not self.simulation_days:
            raise SummaryDataError(f"Summary vector {self.name!r} contains no values")

        start = self.simulation_days[0]
        end = self.simulation_days[-1]
        days: list[float] = []
        current = start
        while current <= end:
            days.append(current)
            current += interval
        if days[-1] != end:
            days.append(end)

        return SummaryVector(
            key=self.key,
            values=tuple(self.interpolate_at(day) for day in days),
            simulation_days=tuple(days),
            report_steps=tuple(range(len(days))),
            dates=self._dates_for_days(days),
            unit=self.unit,
        )

    def to_numpy(self) -> object:
        """Return vector values as a NumPy array when NumPy is installed."""

        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError as error:
            raise UnsupportedFormatError("NumPy is not installed") from error
        return np.asarray(self.values, dtype=float)

    def _dates_for_days(self, days: Sequence[float]) -> tuple[date, ...]:
        if not self.dates:
            return ()
        start_date = self.dates[0]
        start_day = self.simulation_days[0]
        return tuple(
            start_date + timedelta(days=round(day - start_day))
            for day in days
        )

    def _value_at_offset(self, index: int) -> float:
        if not self.values:
            raise SummaryDataError(f"Summary vector {self.name!r} contains no values")
        return self.values[index]
