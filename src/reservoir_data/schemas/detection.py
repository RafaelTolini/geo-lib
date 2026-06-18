"""Detection DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory, FileFormat
from reservoir_data.exceptions.errors import UnsupportedFormatError


@dataclass(frozen=True, slots=True)
class FormatDetectionResult:
    """Result of filename or payload-based format detection."""

    path: Path
    file_category: FileCategory
    formatted: bool | None
    unified: bool | None
    report_step: int | None
    confidence: float
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "file_category", FileCategory(self.file_category))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        if self.report_step is not None and self.report_step < 0:
            raise ValueError("report_step must be non-negative when provided")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_file_format(self) -> FileFormat:
        """Return a path-independent format value object."""

        return FileFormat(
            file_category=self.file_category,
            formatted=self.formatted,
            unified=self.unified,
            report_step=self.report_step,
        )

    @property
    def format_label(self) -> str:
        """Return a human-readable payload format label."""

        if self.formatted is True:
            return "formatted"
        if self.formatted is False:
            return "unformatted"
        return "unknown"

    def diagnostic_summary(self) -> str:
        """Return diagnostics as one compact message."""

        return "; ".join(self.diagnostics)

    def to_row(self) -> dict[str, object]:
        """Return a tabular representation of this detection result."""

        return {
            "PATH": str(self.path),
            "FILE_NAME": self.path.name,
            "CATEGORY": self.file_category.value,
            "FORMAT": self.format_label,
            "FORMATTED": self.formatted,
            "UNIFIED": self.unified,
            "REPORT_STEP": self.report_step,
            "CONFIDENCE": self.confidence,
            "DIAGNOSTICS": self.diagnostic_summary(),
        }

    def require_formatted(self, context: str = "this operation") -> None:
        """Raise when the detected file is not explicitly formatted."""

        if self.formatted is not True:
            raise UnsupportedFormatError(
                f"{context} requires a formatted file; detected "
                f"{self.format_label} payload for {self.path}"
            )
