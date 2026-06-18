"""Application service for summary workflows."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.summary.summary_dataset import SummaryDataset
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.formats.summary.formatted_summary_reader import (
    FormattedSummaryReader,
)
from reservoir_data.infrastructure.caching.json_index_cache import JsonIndexCache
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import (
    CachePolicy,
    FormattedFilePreference,
    SummaryKeySeparatorPolicy,
    SummaryLoadOptions,
    SummaryTimeUnitPolicy,
)


@dataclass(frozen=True, slots=True)
class SummaryService:
    """Coordinate summary loading from a case manifest."""

    summary_reader: FormattedSummaryReader = field(
        default_factory=FormattedSummaryReader
    )

    def load_summary(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
        cache_policy: CachePolicy = CachePolicy.DISABLED,
        options: SummaryLoadOptions | None = None,
    ) -> SummaryDataset:
        """Load supported formatted summary metadata and vector indexes."""

        resolved_options = options or SummaryLoadOptions()
        self._validate_summary_options(resolved_options)
        metadata_detection = self._select_metadata(manifest, preference)
        data_detections = self._select_data(manifest, preference)
        dataset = self.summary_reader.read(
            metadata_detection.path,
            data_detections,
            cache=self._cache_store(manifest, cache_policy),
        )
        if resolved_options.vector_filter:
            dataset = dataset.select(resolved_options.vector_filter)
        if not resolved_options.lazy_vectors:
            dataset.vectors()
        return dataset

    def load_summary_from_paths(
        self,
        metadata_path: str | Path,
        data_paths: Iterable[str | Path],
        report_steps: Iterable[int] | None = None,
        options: SummaryLoadOptions | None = None,
    ) -> SummaryDataset:
        """Load formatted summary data from explicit metadata and data paths."""

        resolved_options = options or SummaryLoadOptions()
        self._validate_summary_options(resolved_options)
        paths = tuple(Path(path) for path in data_paths)
        if not paths:
            raise FileReadError("No summary data paths were provided")

        steps = None if report_steps is None else tuple(int(step) for step in report_steps)
        if steps is not None and len(steps) != len(paths):
            raise ValueError("report_steps must match the number of data paths")

        data_detections = tuple(
            FormatDetectionResult(
                path=path,
                file_category=FileCategory.SUMMARY_DATA,
                formatted=True,
                unified=steps is None,
                report_step=None if steps is None else steps[index],
                confidence=1.0,
                diagnostics=("Explicit summary data path.",),
            )
            for index, path in enumerate(paths)
        )
        dataset = self.summary_reader.read(metadata_path, data_detections)
        if resolved_options.vector_filter:
            dataset = dataset.select(resolved_options.vector_filter)
        if not resolved_options.lazy_vectors:
            dataset.vectors()
        return dataset

    def _validate_summary_options(self, options: SummaryLoadOptions) -> None:
        if options.include_restart_metadata:
            raise UnsupportedFormatError(
                "Including restart metadata while loading summary data is not implemented"
            )
        if options.key_separator_policy is not SummaryKeySeparatorPolicy.COLON:
            raise UnsupportedFormatError(
                "Only colon-separated summary vector keys are supported"
            )
        if options.time_unit_policy is not SummaryTimeUnitPolicy.DAYS:
            raise UnsupportedFormatError(
                "Only simulation-day summary time axes are supported"
            )
        if not options.strict_metadata_validation:
            raise UnsupportedFormatError(
                "Relaxed summary metadata validation is not implemented"
            )

    def _select_metadata(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference,
    ) -> FormatDetectionResult:
        metadata = manifest.files_for(FileCategory.SUMMARY_METADATA)
        if not metadata:
            raise FileReadError(
                f"No summary metadata files were discovered for case "
                f"'{manifest.case_name}'"
            )
        normalized_preference = FormattedFilePreference(preference)
        if normalized_preference is FormattedFilePreference.UNFORMATTED:
            raise UnsupportedFormatError(
                "Unformatted summary metadata decoding is not implemented"
            )

        formatted = tuple(item for item in metadata if item.formatted is True)
        if not formatted:
            raise UnsupportedFormatError(
                "Only formatted summary metadata files are supported by the current "
                "summary reader"
            )
        return sorted(formatted, key=lambda item: item.path.name.casefold())[0]

    def _select_data(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference,
    ) -> tuple[FormatDetectionResult, ...]:
        data = manifest.files_for(FileCategory.SUMMARY_DATA)
        if not data:
            raise FileReadError(
                f"No summary data files were discovered for case "
                f"'{manifest.case_name}'"
            )
        normalized_preference = FormattedFilePreference(preference)
        if normalized_preference is FormattedFilePreference.UNFORMATTED:
            raise UnsupportedFormatError(
                "Unformatted summary vector decoding is not implemented"
            )

        formatted = tuple(item for item in data if item.formatted is True)
        if not formatted:
            raise UnsupportedFormatError(
                "Only formatted summary data files are supported by the current "
                "summary reader"
            )

        unified = tuple(item for item in formatted if item.unified is True)
        selected = unified if unified else tuple(
            item for item in formatted if item.unified is False
        )
        return tuple(sorted(selected, key=self._detection_sort_key))

    def _detection_sort_key(self, detection: FormatDetectionResult) -> tuple[int, str]:
        step = detection.report_step if detection.report_step is not None else -1
        return step, detection.path.name.casefold()

    def _cache_store(
        self,
        manifest: CaseManifest,
        cache_policy: CachePolicy,
    ) -> JsonIndexCache | None:
        normalized_policy = CachePolicy(cache_policy)
        if normalized_policy is CachePolicy.DISABLED:
            return None
        return JsonIndexCache(
            cache_dir=manifest.root_path / ".reservoir_data_cache",
            writable=normalized_policy is CachePolicy.READ_WRITE,
        )
