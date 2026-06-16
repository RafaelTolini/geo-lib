"""Detection DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory, FileFormat


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
