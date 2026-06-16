"""Detected file format value objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FileCategory(StrEnum):
    """High-level reservoir file categories recognized by discovery."""

    DECK = "deck"
    GRDECL = "grdecl"
    GRID = "grid"
    INIT = "init"
    RESTART = "restart"
    SUMMARY_METADATA = "summary_metadata"
    SUMMARY_DATA = "summary_data"
    RFT = "rft"
    PLT = "plt"


@dataclass(frozen=True, slots=True)
class FileFormat:
    """Neutral description of a detected reservoir file format."""

    file_category: FileCategory
    formatted: bool | None = None
    unified: bool | None = None
    report_step: int | None = None

    def __post_init__(self) -> None:
        if self.report_step is not None and self.report_step < 0:
            raise ValueError("report_step must be non-negative when provided")
