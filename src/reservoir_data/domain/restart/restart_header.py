"""Restart report header metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class RestartHeader:
    """Metadata for one restart report step."""

    report_step: int
    sequence_index: int
    simulation_days: float | None = None
    report_date: date | None = None
    source: str | None = None
    unified: bool | None = None

    def __post_init__(self) -> None:
        if self.report_step < 0:
            raise ValueError("report_step must be non-negative")
        if self.sequence_index < 0:
            raise ValueError("sequence_index must be non-negative")
