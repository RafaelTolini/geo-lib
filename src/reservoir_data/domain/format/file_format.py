"""File format value objects used by discovery and manifests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FileCategory(str, Enum):
    """Supported high-level file roles discovered in a simulation case."""

    DECK = "deck"
    GRDECL = "grdecl"
    GRID = "grid"
    INIT = "init"
    RESTART = "restart"
    SUMMARY_SPEC = "summary_spec"
    SUMMARY_DATA = "summary_data"
    RFT = "rft"
    UNKNOWN = "unknown"

    @property
    def public_data_name(self) -> str:
        """Return the user-facing data group exposed by case facades."""

        if self is FileCategory.INIT:
            return "properties"
        if self in {FileCategory.SUMMARY_SPEC, FileCategory.SUMMARY_DATA}:
            return "summary"
        return self.value


@dataclass(frozen=True, slots=True)
class FileFormat:
    """Detected category and encoding style for a reservoir data file."""

    category: FileCategory
    formatted: bool | None = None
    unified: bool | None = None
    report_step: int | None = None
    confidence: float = 1.0
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "category", FileCategory(self.category))
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.report_step is not None and self.report_step < 0:
            raise ValueError("report_step must be non-negative")
