"""Application service for case file discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Union

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.exceptions.errors import FileDetectionError, FileReadError
from reservoir_data.formats.common.file_detector import FileDetector
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import LoadCaseOptions

CasePath = Union[str, Path]


@dataclass(slots=True)
class FileCatalog:
    """Discovers recognized files belonging to one simulation case."""

    detector: FileDetector = field(default_factory=FileDetector)

    def discover(
        self, path_or_basename: CasePath, options: LoadCaseOptions | None = None
    ) -> CaseManifest:
        """Discover files for an explicit file, basename, or unambiguous directory."""

        resolved_options = options or LoadCaseOptions()
        requested = self._requested_path(path_or_basename, resolved_options)

        if requested.exists() and requested.is_dir():
            return self._discover_directory(requested, resolved_options)

        if requested.exists() and requested.is_file():
            explicit_detection = self.detector.detect(requested)
            base_name = requested.stem
            root_path = requested.parent
            detections = self._discover_for_basename(
                root_path, base_name, resolved_options
            )
            if self._is_allowed(explicit_detection, resolved_options):
                detections = self._include_detection(detections, explicit_detection)
            return self._manifest_from_detections(
                base_name,
                root_path,
                detections,
                (f"Opened from explicit file: {requested.name}",),
                resolved_options,
            )

        if requested.suffix:
            raise FileReadError(f"Case file does not exist: {requested}")

        root_path = requested.parent
        if not root_path.exists() or not root_path.is_dir():
            raise FileReadError(f"Case root directory does not exist: {root_path}")

        detections = self._discover_for_basename(
            root_path, requested.name, resolved_options
        )
        if not detections and resolved_options.strict_discovery:
            raise FileReadError(
                f"No recognizable files were found for case basename "
                f"'{requested.name}' in {root_path}"
            )
        return self._manifest_from_detections(
            requested.name,
            root_path,
            detections,
            ("Opened from case basename.",),
            resolved_options,
        )

    def _requested_path(self, path_or_basename: CasePath, options: LoadCaseOptions) -> Path:
        requested = Path(path_or_basename).expanduser()
        if not requested.is_absolute() and options.root_path is not None:
            requested = options.root_path / requested
        return requested

    def _discover_directory(
        self, directory: Path, options: LoadCaseOptions
    ) -> CaseManifest:
        detections_by_case: dict[str, list[FormatDetectionResult]] = {}
        diagnostics: list[str] = [f"Opened from directory: {directory}"]

        for detection in self._detect_recognized_files(directory.iterdir(), options):
            detections_by_case.setdefault(detection.path.stem.casefold(), []).append(
                detection
            )

        if not detections_by_case:
            if options.strict_discovery:
                raise FileDetectionError(
                    f"No recognizable reservoir data files were found in {directory}"
                )
            return CaseManifest(
                case_name=directory.name,
                root_path=directory,
                files=(),
                diagnostics=tuple(diagnostics),
            )

        selected_key = self._select_case_key(directory.name, detections_by_case, options)
        case_name = self._display_case_name(detections_by_case[selected_key])
        return self._manifest_from_detections(
            case_name,
            directory,
            tuple(detections_by_case[selected_key]),
            tuple(diagnostics),
            options,
        )

    def _discover_for_basename(
        self, root_path: Path, basename: str, options: LoadCaseOptions
    ) -> tuple[FormatDetectionResult, ...]:
        if not root_path.exists() or not root_path.is_dir():
            raise FileReadError(f"Case root directory does not exist: {root_path}")

        requested_key = basename.casefold()
        detections = [
            detection
            for detection in self._detect_recognized_files(root_path.iterdir(), options)
            if detection.path.stem.casefold() == requested_key
        ]
        return tuple(detections)

    def _detect_recognized_files(
        self, paths: Iterable[Path], options: LoadCaseOptions
    ) -> tuple[FormatDetectionResult, ...]:
        detections: list[FormatDetectionResult] = []
        for path in paths:
            if not path.is_file():
                continue
            try:
                detection = self.detector.detect(path)
            except FileDetectionError:
                continue
            if self._is_allowed(detection, options):
                detections.append(detection)
        return tuple(sorted(detections, key=lambda item: item.path.name.casefold()))

    def _is_allowed(
        self, detection: FormatDetectionResult, options: LoadCaseOptions
    ) -> bool:
        if options.file_categories is None:
            return True
        return detection.file_category in options.file_categories

    def _select_case_key(
        self,
        directory_name: str,
        detections_by_case: dict[str, list[FormatDetectionResult]],
        options: LoadCaseOptions,
    ) -> str:
        if len(detections_by_case) == 1:
            return next(iter(detections_by_case))

        directory_key = directory_name.casefold()
        if directory_key in detections_by_case:
            return directory_key

        if options.strict_discovery:
            cases = ", ".join(sorted(detections_by_case))
            raise FileDetectionError(
                f"Directory contains multiple possible case basenames: {cases}"
            )
        return sorted(detections_by_case)[0]

    def _manifest_from_detections(
        self,
        case_name: str,
        root_path: Path,
        detections: tuple[FormatDetectionResult, ...],
        diagnostics: tuple[str, ...],
        options: LoadCaseOptions,
    ) -> CaseManifest:
        if not detections and options.strict_discovery:
            raise FileDetectionError(
                f"No recognized files are available for case '{case_name}'"
            )
        return CaseManifest(
            case_name=case_name,
            root_path=root_path,
            files=detections,
            diagnostics=diagnostics,
        )

    def _include_detection(
        self,
        detections: tuple[FormatDetectionResult, ...],
        detection: FormatDetectionResult,
    ) -> tuple[FormatDetectionResult, ...]:
        if any(existing.path == detection.path for existing in detections):
            return detections
        return tuple(sorted((*detections, detection), key=lambda item: item.path.name))

    def _display_case_name(
        self, detections: list[FormatDetectionResult]
    ) -> str:
        return detections[0].path.stem
