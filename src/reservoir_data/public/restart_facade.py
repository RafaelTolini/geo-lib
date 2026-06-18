"""Public restart facade exports."""

from reservoir_data.domain.restart import (
    RestartDataset,
    RestartHeader,
    RestartReport,
)
from reservoir_data.schemas.loading import (
    RestartGridAssociationMode,
    RestartLoadOptions,
)
from reservoir_data.schemas.queries import ReportStepMatchPolicy, ReportStepQuery


def load_restarts_from_paths(
    paths,
    report_steps=None,
    grid=None,
    options: RestartLoadOptions | None = None,
) -> RestartDataset:
    """Load formatted restart data from explicit paths."""

    from reservoir_data.application.restart_service import RestartService

    return RestartService().load_restarts_from_paths(
        paths,
        report_steps=report_steps,
        grid=grid,
        options=options,
    )


__all__ = [
    "load_restarts_from_paths",
    "ReportStepMatchPolicy",
    "ReportStepQuery",
    "RestartDataset",
    "RestartGridAssociationMode",
    "RestartHeader",
    "RestartLoadOptions",
    "RestartReport",
]
