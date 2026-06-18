"""Discovered files belonging to a simulation case."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import FormattedFilePreference


@dataclass(frozen=True, slots=True)
class CaseManifest:
    """Describes recognized files discovered for one case basename."""

    case_name: str
    root_path: Path
    files: tuple[FormatDetectionResult, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "root_path", Path(self.root_path))
        object.__setattr__(
            self,
            "files",
            tuple(sorted(self.files, key=lambda item: item.path.name.casefold())),
        )
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

    def available_categories(self) -> tuple[FileCategory, ...]:
        """Return discovered file categories in stable order."""

        return tuple(sorted({item.file_category for item in self.files}, key=str))

    def has_category(self, category: FileCategory) -> bool:
        """Return whether a category was discovered."""

        return any(item.file_category == category for item in self.files)

    def files_for(self, category: FileCategory) -> tuple[FormatDetectionResult, ...]:
        """Return all detected files for a category."""

        return tuple(item for item in self.files if item.file_category == category)

    def file_rows(self) -> tuple[dict[str, object], ...]:
        """Return discovered file rows for diagnostics and export."""

        return tuple(item.to_row() for item in self.files)

    def files_to_csv(self, path: str | Path) -> None:
        """Write discovered file rows to CSV."""

        fieldnames = [
            "PATH",
            "FILE_NAME",
            "CATEGORY",
            "FORMAT",
            "FORMATTED",
            "UNIFIED",
            "REPORT_STEP",
            "CONFIDENCE",
            "DIAGNOSTICS",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.file_rows())

    def preferred_file(
        self,
        category: FileCategory,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> FormatDetectionResult | None:
        """Resolve a preferred file for a category without parsing payloads."""

        candidates = self.files_for(category)
        if not candidates:
            return None

        if preference is FormattedFilePreference.FORMATTED:
            formatted = tuple(item for item in candidates if item.formatted is True)
            if formatted:
                return formatted[0]
        elif preference is FormattedFilePreference.UNFORMATTED:
            unformatted = tuple(item for item in candidates if item.formatted is False)
            if unformatted:
                return unformatted[0]

        unified = tuple(item for item in candidates if item.unified is True)
        if unified:
            return unified[0]
        return candidates[0]
