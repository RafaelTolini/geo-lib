from datetime import date
from pathlib import Path

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import (
    MissingKeywordError,
    ParseError,
    SummaryDataError,
    UnsupportedFormatError,
)
from reservoir_data.formats.summary.formatted_summary_reader import (
    FormattedSummaryReader,
)
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.detection import FormatDetectionResult


def _metadata_text() -> str:
    return """
    VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /
    VECTOR 'FOPT' 'SM3' 'FIELD' /
    VECTOR 'WOPR' 'SM3/DAY' 'WELL' 'PROD-1' /
    """


def _unified_data_text() -> str:
    return """
    TIME 0 10 20 /
    DATES '2026-01-01' '2026-01-11' '2026-01-21' /
    REPORTS 0 1 2 /
    VALUES 'FOPR' 100 120 160 /
    VALUES 'FOPT' 0 1000 2400 /
    VALUES 'WOPR:PROD-1' 30 40 50 /
    """


def _summary_detection(
    path: Path,
    category: FileCategory = FileCategory.SUMMARY_DATA,
    unified: bool = True,
    report_step: int | None = None,
) -> FormatDetectionResult:
    return FormatDetectionResult(
        path=path,
        file_category=category,
        formatted=True,
        unified=unified,
        report_step=report_step,
        confidence=1.0,
        diagnostics=("test fixture",),
    )


def test_formatted_summary_reader_indexes_metadata_and_vectors_lazily(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "CASE.FSMSPEC"
    data_path = tmp_path / "CASE.FUNSMRY"
    metadata_path.write_text(_metadata_text(), encoding="utf-8")
    data_path.write_text(_unified_data_text(), encoding="utf-8")

    dataset = FormattedSummaryReader().read(
        metadata_path,
        (_summary_detection(data_path),),
    )

    assert dataset.unified is True
    assert dataset.keys() == ("FOPR", "FOPT", "WOPR:PROD-1")
    assert dataset.filter_keys("WO*", qualifier_kind="well") == ("WOPR:PROD-1",)
    assert dataset.simulation_days == (0.0, 10.0, 20.0)
    assert dataset.report_steps == (0, 1, 2)
    assert dataset.dates == (
        date(2026, 1, 1),
        date(2026, 1, 11),
        date(2026, 1, 21),
    )

    assert not dataset.is_vector_loaded("FOPR")
    vector = dataset.vector("FOPR")
    assert dataset.is_vector_loaded("FOPR")
    assert vector.unit == "SM3/DAY"
    assert vector.values == (100.0, 120.0, 160.0)
    assert vector.first_value() == 100.0
    assert vector.last_value() == 160.0
    assert vector.value_at_report_step(1) == 120.0


def test_summary_vector_interpolation_resampling_and_export_boundaries(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "CASE.FSMSPEC"
    data_path = tmp_path / "CASE.FUNSMRY"
    csv_path = tmp_path / "summary.csv"
    metadata_path.write_text(_metadata_text(), encoding="utf-8")
    data_path.write_text(_unified_data_text(), encoding="utf-8")
    dataset = FormattedSummaryReader().read(
        metadata_path,
        (_summary_detection(data_path),),
    )

    vector = dataset.vector("FOPR")
    resampled = vector.resample(interval_days=5)

    assert vector.interpolate_at(5) == 110.0
    assert resampled.simulation_days == (0.0, 5.0, 10.0, 15.0, 20.0)
    assert resampled.values == (100.0, 110.0, 120.0, 140.0, 160.0)

    dataset.to_csv(csv_path, keys=["FOPR", "FOPT"])
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "DATE,REPORT_STEP,SIMULATION_DAYS,FOPR,FOPT" in csv_text
    assert "2026-01-11,1,10.0,120.0,1000.0" in csv_text

    try:
        numpy_arrays = dataset.to_numpy(keys=["FOPR"])
    except UnsupportedFormatError:
        pass
    else:
        assert tuple(numpy_arrays["FOPR"]) == (100.0, 120.0, 160.0)

    try:
        frame = dataset.to_pandas(keys=["FOPR"])
    except UnsupportedFormatError:
        pass
    else:
        assert list(frame["FOPR"]) == [100.0, 120.0, 160.0]


def test_public_case_loads_formatted_unified_summary(tmp_path: Path) -> None:
    (tmp_path / "CASE.FSMSPEC").write_text(_metadata_text(), encoding="utf-8")
    (tmp_path / "CASE.FUNSMRY").write_text(_unified_data_text(), encoding="utf-8")

    dataset = SimulationCase.open(tmp_path / "CASE").load_summary()

    assert dataset.keys() == ("FOPR", "FOPT", "WOPR:PROD-1")
    assert dataset.vector("WOPR:PROD-1").values == (30.0, 40.0, 50.0)


def test_public_case_groups_formatted_non_unified_summary(tmp_path: Path) -> None:
    (tmp_path / "CASE.FSMSPEC").write_text(
        "VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /",
        encoding="utf-8",
    )
    (tmp_path / "CASE.A0002").write_text(
        """
        TIME 20 /
        DATES '2026-01-21' /
        VALUES 'FOPR' 160 /
        """,
        encoding="utf-8",
    )
    (tmp_path / "CASE.A0001").write_text(
        """
        TIME 10 /
        DATES '2026-01-11' /
        VALUES 'FOPR' 120 /
        """,
        encoding="utf-8",
    )

    dataset = SimulationCase.open(tmp_path / "CASE").load_summary()

    assert dataset.unified is False
    assert dataset.report_steps == (1, 2)
    assert dataset.vector("FOPR").values == (120.0, 160.0)


def test_summary_reader_reports_missing_and_corrupt_data(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "CASE.FSMSPEC"
    data_path = tmp_path / "CASE.FUNSMRY"
    metadata_path.write_text("VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /", encoding="utf-8")
    data_path.write_text(
        """
        TIME 0 10 /
        DATES '2026-01-01' '2026-01-11' /
        REPORTS 0 1 /
        VALUES 'FOPR' 100 /
        """,
        encoding="utf-8",
    )
    dataset = FormattedSummaryReader().read(
        metadata_path,
        (_summary_detection(data_path),),
    )

    with pytest.raises(MissingKeywordError):
        dataset.vector("NOPE")
    with pytest.raises(SummaryDataError, match="expected 2"):
        dataset.vector("FOPR")

    data_path.write_bytes(b"\x04\x00\x00\x00ABCD\x04\x00\x00\x00")
    with pytest.raises(ParseError, match="binary-looking"):
        FormattedSummaryReader().read(
            metadata_path,
            (_summary_detection(data_path),),
        )
