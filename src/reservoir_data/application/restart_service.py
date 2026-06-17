"""Application service for restart workflows."""

from __future__ import annotations

from dataclasses import dataclass, field

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.restart.restart_dataset import RestartDataset
from reservoir_data.domain.restart.restart_header import RestartHeader
from reservoir_data.domain.restart.restart_report import RestartReport
from reservoir_data.exceptions.errors import (
    FileReadError,
    InvalidReportStepError,
    UnsupportedFormatError,
)
from reservoir_data.formats.restart.formatted_restart_reader import (
    FormattedRestartReader,
)
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import FormattedFilePreference, RestartLoadOptions


@dataclass(frozen=True, slots=True)
class RestartService:
    """Coordinate restart loading from a case manifest."""

    restart_reader: FormattedRestartReader = field(
        default_factory=FormattedRestartReader
    )

    def load_restarts(
        self,
        manifest: CaseManifest,
        grid: ReservoirGrid | None = None,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
        options: RestartLoadOptions | None = None,
    ) -> RestartDataset:
        """Load supported formatted restart indexes and lazy report payloads."""

        resolved_options = options or RestartLoadOptions()
        self._validate_restart_options(resolved_options)
        detections = self._select_supported_detections(manifest, preference)
        datasets = tuple(
            self.restart_reader.read(detection.path, detection=detection)
            for detection in detections
        )
        reports: list[RestartReport] = []
        sources: list[str] = []
        for dataset in datasets:
            sources.extend(dataset.sources)
            reports.extend(dataset.reports)

        ordered_reports = sorted(
            reports,
            key=lambda report: (report.report_step, report.header.source or ""),
        )
        renumbered = tuple(
            self._with_sequence(report, sequence_index)
            for sequence_index, report in enumerate(ordered_reports)
        )
        unified = all(detection.unified is True for detection in detections)
        dataset = RestartDataset(
            reports=renumbered,
            sources=tuple(sources),
            unified=unified,
            grid=grid,
        )
        dataset = self._filter_report_steps(
            dataset,
            resolved_options.requested_report_steps,
        )
        if grid is not None:
            dataset = dataset.with_grid(grid)
        if not resolved_options.header_only and not resolved_options.lazy_keyword_arrays:
            for report in dataset.reports:
                _ = report.keywords
        return dataset

    def _validate_restart_options(self, options: RestartLoadOptions) -> None:
        if options.load_well_data:
            raise UnsupportedFormatError(
                "Restart well-data extraction is exposed through load_wells(); "
                "RestartLoadOptions.load_well_data is not implemented"
            )

    def _select_supported_detections(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference,
    ) -> tuple[FormatDetectionResult, ...]:
        detections = manifest.files_for(FileCategory.RESTART)
        if not detections:
            raise FileReadError(
                f"No restart files were discovered for case '{manifest.case_name}'"
            )

        normalized_preference = FormattedFilePreference(preference)
        if normalized_preference is FormattedFilePreference.UNFORMATTED:
            raise UnsupportedFormatError(
                "Unformatted restart keyword payload decoding is not implemented"
            )

        formatted = tuple(
            detection for detection in detections if detection.formatted is True
        )
        if not formatted:
            raise UnsupportedFormatError(
                "Only formatted restart keyword files are supported by the current "
                "restart reader"
            )

        unified = tuple(detection for detection in formatted if detection.unified is True)
        selected = unified if unified else tuple(
            detection for detection in formatted if detection.unified is False
        )
        return tuple(sorted(selected, key=self._detection_sort_key))

    def _detection_sort_key(self, detection: FormatDetectionResult) -> tuple[int, str]:
        step = detection.report_step if detection.report_step is not None else -1
        return step, detection.path.name.casefold()

    def _with_sequence(
        self, report: RestartReport, sequence_index: int
    ) -> RestartReport:
        header = RestartHeader(
            report_step=report.header.report_step,
            sequence_index=sequence_index,
            simulation_days=report.header.simulation_days,
            report_date=report.header.report_date,
            source=report.header.source,
            unified=report.header.unified,
        )
        return report.with_header(header)

    def _filter_report_steps(
        self,
        dataset: RestartDataset,
        requested_steps: tuple[int, ...] | None,
    ) -> RestartDataset:
        if requested_steps is None:
            return dataset

        available = {report.report_step: report for report in dataset.reports}
        missing = tuple(step for step in requested_steps if step not in available)
        if missing:
            raise InvalidReportStepError(
                f"Requested restart report step {missing[0]} was not found"
            )
        selected = tuple(
            self._with_sequence(available[step], sequence_index)
            for sequence_index, step in enumerate(requested_steps)
        )
        return RestartDataset(
            reports=selected,
            sources=dataset.sources,
            unified=dataset.unified,
            grid=dataset.grid,
        )
