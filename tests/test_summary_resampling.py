from datetime import date

import pytest

from reservoir_data.domain.summary import SummaryInterpolationMethod, SummaryKey
from reservoir_data.domain.summary.summary_vector import SummaryVector
from reservoir_data.exceptions.errors import InvalidReportStepError
from reservoir_data.public.summary_facade import (
    SummaryInterpolationMethod as PublicSummaryInterpolationMethod,
)


def _vector() -> SummaryVector:
    return SummaryVector(
        key=SummaryKey.parse("FOPR"),
        values=(100.0, 160.0, 220.0),
        simulation_days=(0.0, 10.0, 20.0),
        report_steps=(0, 1, 2),
        dates=(date(2026, 1, 1), date(2026, 1, 11), date(2026, 1, 21)),
        unit="SM3/DAY",
    )


def test_summary_vector_interpolation_method_defaults_to_linear() -> None:
    vector = _vector()

    assert vector.interpolate_at(5.0) == 130.0
    assert vector.interpolate_at(5.0, method=SummaryInterpolationMethod.LINEAR) == 130.0
    assert vector.resample(5.0).values == (100.0, 130.0, 160.0, 190.0, 220.0)


def test_summary_vector_stepwise_interpolation_and_resampling() -> None:
    vector = _vector()

    assert vector.interpolate_at(5.0, method=SummaryInterpolationMethod.STEPWISE) == 100.0
    assert vector.interpolate_at(10.0, method="stepwise") == 160.0
    assert vector.resample(5.0, method="stepwise").values == (
        100.0,
        100.0,
        160.0,
        160.0,
        220.0,
    )


def test_summary_interpolation_rejects_unknown_methods_and_out_of_range_days() -> None:
    vector = _vector()

    with pytest.raises(ValueError):
        vector.interpolate_at(5.0, method="nearest")
    with pytest.raises(InvalidReportStepError):
        vector.interpolate_at(25.0, method=SummaryInterpolationMethod.STEPWISE)


def test_public_summary_facade_exports_interpolation_method() -> None:
    assert PublicSummaryInterpolationMethod is SummaryInterpolationMethod
