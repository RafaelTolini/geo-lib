"""Public summary facade exports."""

from reservoir_data.domain.summary import (
    SummaryDataset,
    SummaryInterpolationMethod,
    SummaryKey,
    SummaryMetadata,
    SummaryVector,
    SummaryVectorMetadata,
)
from reservoir_data.schemas.loading import (
    SummaryKeySeparatorPolicy,
    SummaryLoadOptions,
    SummaryTimeUnitPolicy,
)
from reservoir_data.schemas.queries import ReportStepMatchPolicy, ReportStepQuery


def load_summary_from_paths(
    metadata_path,
    data_paths,
    report_steps=None,
    options: SummaryLoadOptions | None = None,
) -> SummaryDataset:
    """Load formatted summary data from explicit metadata and data paths."""

    from reservoir_data.application.summary_service import SummaryService

    return SummaryService().load_summary_from_paths(
        metadata_path,
        data_paths,
        report_steps=report_steps,
        options=options,
    )


__all__ = [
    "load_summary_from_paths",
    "ReportStepMatchPolicy",
    "ReportStepQuery",
    "SummaryDataset",
    "SummaryInterpolationMethod",
    "SummaryKey",
    "SummaryKeySeparatorPolicy",
    "SummaryLoadOptions",
    "SummaryMetadata",
    "SummaryTimeUnitPolicy",
    "SummaryVector",
    "SummaryVectorMetadata",
]
