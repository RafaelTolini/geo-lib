from datetime import date

import pytest

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.restart import RestartDataset, RestartHeader, RestartReport
from reservoir_data.domain.summary import (
    SummaryDataset,
    SummaryKey,
    SummaryMetadata,
    SummaryVector,
    SummaryVectorMetadata,
)
from reservoir_data.domain.well import WellSnapshot, WellTimeline
from reservoir_data.exceptions.errors import InvalidReportStepError
from reservoir_data.schemas.queries import ReportStepMatchPolicy, ReportStepQuery


def _restart_dataset() -> RestartDataset:
    def empty_keywords() -> KeywordDataset:
        return KeywordDataset()

    return RestartDataset(
        reports=(
            RestartReport(
                header=RestartHeader(
                    report_step=1,
                    sequence_index=0,
                    simulation_days=10.0,
                    report_date=date(2026, 1, 10),
                ),
                _keyword_loader=empty_keywords,
            ),
            RestartReport(
                header=RestartHeader(
                    report_step=4,
                    sequence_index=1,
                    simulation_days=40.0,
                    report_date=date(2026, 2, 9),
                ),
                _keyword_loader=empty_keywords,
            ),
        )
    )


def _summary_dataset() -> SummaryDataset:
    metadata = SummaryMetadata(
        vectors=(
            SummaryVectorMetadata(
                key=SummaryKey.parse("FOPR"),
                unit="SM3/DAY",
                classification="field",
            ),
        )
    )
    vector = SummaryVector(
        key=SummaryKey.parse("FOPR"),
        simulation_days=(10.0, 40.0),
        report_steps=(1, 4),
        dates=(date(2026, 1, 10), date(2026, 2, 9)),
        values=(100.0, 400.0),
        unit="SM3/DAY",
    )
    return SummaryDataset(
        metadata=metadata,
        simulation_days=(10.0, 40.0),
        report_steps=(1, 4),
        dates=(date(2026, 1, 10), date(2026, 2, 9)),
        _vector_loaders={"FOPR": lambda: vector},
    )


def _well_timeline() -> WellTimeline:
    return WellTimeline(
        well_name="PROD-1",
        snapshots=(
            WellSnapshot(
                well_name="PROD-1",
                report_step=1,
                well_type="producer",
                is_open=True,
                simulation_days=10.0,
                report_date=date(2026, 1, 10),
            ),
            WellSnapshot(
                well_name="PROD-1",
                report_step=4,
                well_type="producer",
                is_open=False,
                simulation_days=40.0,
                report_date=date(2026, 2, 9),
            ),
        ),
    )


def test_restart_dataset_query_supports_exact_and_nearest_policy() -> None:
    dataset = _restart_dataset()

    assert dataset.query(ReportStepQuery(report_step=1)).report_step == 1
    assert (
        dataset.query(
            ReportStepQuery(
                simulation_days=35.0,
                match_policy=ReportStepMatchPolicy.NEAREST,
            )
        ).report_step
        == 4
    )
    assert (
        dataset.query(
            ReportStepQuery(
                report_date=date(2026, 1, 20),
                match_policy=ReportStepMatchPolicy.NEAREST,
            )
        ).report_step
        == 1
    )

    with pytest.raises(InvalidReportStepError):
        dataset.query(ReportStepQuery(simulation_days=35.0))


def test_summary_dataset_query_returns_exact_or_nearest_time_index() -> None:
    dataset = _summary_dataset()

    assert dataset.time_index(ReportStepQuery(sequence_index=1)) == 1
    assert dataset.time_index(ReportStepQuery(report_step=4)) == 1
    assert (
        dataset.time_index(
            ReportStepQuery(
                report_date=date(2026, 2, 1),
                match_policy="nearest",
            )
        )
        == 1
    )

    with pytest.raises(InvalidReportStepError):
        dataset.time_index(ReportStepQuery(report_step=3))


def test_well_timeline_query_supports_typed_report_queries() -> None:
    timeline = _well_timeline()

    assert timeline.query(ReportStepQuery(report_step=1)).is_open is True
    assert (
        timeline.query(
            ReportStepQuery(
                simulation_days=30.0,
                match_policy=ReportStepMatchPolicy.NEAREST,
            )
        ).report_step
        == 4
    )
    assert timeline.query(ReportStepQuery(sequence_index=0)).report_step == 1

    with pytest.raises(InvalidReportStepError):
        timeline.query(ReportStepQuery(report_date=date(2026, 1, 15)))
