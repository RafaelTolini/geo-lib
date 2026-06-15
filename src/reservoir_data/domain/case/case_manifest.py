"""Manifest of files discovered for a simulation case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError
from reservoir_data.schemas.detection import FormatDetectionResult


_PUBLIC_DATA_ORDER = (
    "deck",
    "grdecl",
    "grid",
    "properties",
    "restart",
    "summary",
    "rft",
)


@dataclass(frozen=True, slots=True)
class CaseManifest:
    """Discovered files and diagnostics for one simulation case."""

    case_name: str | None
    root_path: Path
    files_by_category: Mapping[FileCategory, tuple[FormatDetectionResult, ...]]
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized: dict[FileCategory, tuple[FormatDetectionResult, ...]] = {}
        for category, detections in self.files_by_category.items():
            normalized[FileCategory(category)] = tuple(detections)
        object.__setattr__(self, "root_path", Path(self.root_path))
        object.__setattr__(self, "files_by_category", MappingProxyType(normalized))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))

    def has_category(self, category: FileCategory | str) -> bool:
        """Return whether this manifest contains the requested file role."""

        return FileCategory(category) in self.files_by_category

    def detections_for(
        self,
        category: FileCategory | str,
    ) -> tuple[FormatDetectionResult, ...]:
        """Return all detected files for a category."""

        return self.files_by_category.get(FileCategory(category), ())

    def available_categories(self) -> tuple[FileCategory, ...]:
        """Return detected categories in stable enum order."""

        return tuple(
            category
            for category in FileCategory
            if category is not FileCategory.UNKNOWN and category in self.files_by_category
        )

    def available_data(self) -> tuple[str, ...]:
        """Return user-facing data groups available for the case."""

        names = {category.public_data_name for category in self.available_categories()}
        return tuple(name for name in _PUBLIC_DATA_ORDER if name in names)

    def preferred_file(
        self,
        category: FileCategory | str,
        *,
        formatted: bool | None = None,
        unified: bool | None = None,
    ) -> FormatDetectionResult:
        """Return a deterministic preferred file for a category."""

        requested = FileCategory(category)
        matches = [
            detection
            for detection in self.detections_for(requested)
            if (formatted is None or detection.formatted == formatted)
            and (unified is None or detection.unified == unified)
        ]
        if not matches:
            raise FileDetectionError(
                f"No discovered file matches category {requested.value!r}"
            )
        return sorted(matches, key=_preferred_sort_key)[0]

    def all_detections(self) -> tuple[FormatDetectionResult, ...]:
        """Return every known detection in deterministic order."""

        detections: list[FormatDetectionResult] = []
        for category in self.available_categories():
            detections.extend(self.files_by_category[category])
        return tuple(sorted(detections, key=lambda detection: str(detection.path).lower()))


def _preferred_sort_key(detection: FormatDetectionResult) -> tuple[int, int, int, str]:
    unified_rank = 0 if detection.unified is True else 1
    report_rank = detection.report_step if detection.report_step is not None else -1
    formatted_rank = 0 if detection.formatted is False else 1
    return (unified_rank, report_rank, formatted_rank, str(detection.path).lower())
