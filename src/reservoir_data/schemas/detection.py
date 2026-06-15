"""Detection DTOs shared by infrastructure, services, and manifests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory


@dataclass(frozen=True, slots=True)
class FormatDetectionResult:
    """Result of identifying a file's reservoir-data role."""

    path: Path
    file_category: FileCategory
    formatted: bool | None = None
    unified: bool | None = None
    report_step: int | None = None
    confidence: float = 1.0
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "file_category", FileCategory(self.file_category))
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.report_step is not None and self.report_step < 0:
            raise ValueError("report_step must be non-negative")

    @property
    def is_known(self) -> bool:
        """Return whether the extension was recognized for discovery."""

        return self.file_category is not FileCategory.UNKNOWN
