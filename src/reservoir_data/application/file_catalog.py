"""Application service for case file discovery."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError, FileReadError, UnsupportedFormatError
from reservoir_data.infrastructure.filesystem.file_detector import FileDetector
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import LoadCaseOptions


@dataclass(frozen=True, slots=True)
class FileCatalog:
    """Discover files belonging to a case basename or directory."""

    detector: FileDetector = field(default_factory=FileDetector)

    def discover(
        self,
        path_or_basename: str | Path,
        options: LoadCaseOptions | None = None,
    ) -> CaseManifest:
        """Discover recognized files without opening simulator payloads."""

        load_options = options or LoadCaseOptions()
        target = _target_path(Path(path_or_basename), load_options)
        target_detection = self.detector.detect(target) if target.suffix else None
        explicit_file_target = (
            target.exists() and target.is_file()
        ) or (
            target_detection is not None and target_detection.is_known
        )
        if explicit_file_target and target.suffix and not target.exists():
            raise FileReadError(f"Requested file does not exist: {target}")
        root_path, case_name = _discovery_scope(target, explicit_file_target)

        if not root_path.exists():
            raise FileReadError(f"Discovery root does not exist: {root_path}")
        if not root_path.is_dir():
            raise FileReadError(f"Discovery root is not a directory: {root_path}")

        detections_by_category: dict[FileCategory, list[FormatDetectionResult]] = defaultdict(list)
        diagnostics: list[str] = []
        basenames: set[str] = set()

        for candidate in sorted(root_path.iterdir(), key=lambda path: path.name.lower()):
            if not candidate.is_file():
                continue
            candidate_case_name = _case_name_from_path(candidate)
            if case_name is not None and candidate_case_name.lower() != case_name.lower():
                continue
            try:
                detection = self.detector.detect(candidate, strict=load_options.strict_discovery)
            except UnsupportedFormatError:
                if case_name is not None:
                    raise
                continue
            if not detection.is_known:
                diagnostics.extend(detection.diagnostics)
                continue
            if not load_options.allows_category(detection.file_category):
                continue
            basenames.add(candidate_case_name)
            detections_by_category[detection.file_category].append(detection)
            diagnostics.extend(detection.diagnostics)

        resolved_case_name = _resolve_case_name(case_name, basenames, load_options)
        if not detections_by_category and load_options.strict_discovery:
            target_label = str(target)
            raise FileDetectionError(f"No recognizable reservoir data files found for {target_label}")

        diagnostics.extend(_multiplicity_diagnostics(detections_by_category))
        return CaseManifest(
            case_name=resolved_case_name,
            root_path=root_path,
            files_by_category={
                category: tuple(sorted(detections, key=lambda item: str(item.path).lower()))
                for category, detections in detections_by_category.items()
            },
            diagnostics=tuple(diagnostics),
        )


def _target_path(path: Path, options: LoadCaseOptions) -> Path:
    if options.root_path is None or path.is_absolute():
        return path
    return options.root_path / path


def _discovery_scope(target: Path, explicit_file_target: bool) -> tuple[Path, str | None]:
    if target.exists() and target.is_dir():
        return (target, None)
    if explicit_file_target:
        return (target.parent if str(target.parent) else Path.cwd(), _case_name_from_path(target))
    return (target.parent if str(target.parent) else Path.cwd(), target.name)


def _case_name_from_path(path: Path) -> str:
    suffix = path.suffix
    if suffix:
        return path.name[: -len(suffix)]
    return path.name


def _resolve_case_name(
    requested_case_name: str | None,
    discovered_basenames: set[str],
    options: LoadCaseOptions,
) -> str | None:
    if requested_case_name is not None:
        return requested_case_name
    if len(discovered_basenames) == 1:
        return next(iter(discovered_basenames))
    if len(discovered_basenames) > 1 and options.strict_discovery:
        names = ", ".join(sorted(discovered_basenames))
        raise FileDetectionError(f"Ambiguous directory discovery; found multiple basenames: {names}")
    return None


def _multiplicity_diagnostics(
    detections_by_category: dict[FileCategory, list[FormatDetectionResult]],
) -> tuple[str, ...]:
    diagnostics: list[str] = []
    for category, detections in detections_by_category.items():
        if len(detections) > 1:
            diagnostics.append(
                f"Multiple {category.value} files discovered; preferred selection is deterministic."
            )
    return tuple(diagnostics)
