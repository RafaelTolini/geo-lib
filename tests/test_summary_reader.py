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
from reservoir_data.public.summary_facade import load_summary_from_paths
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
    assert vector.value_at_time_index(2) == 160.0
    assert vector.value_at_simulation_days(10.0) == 120.0
    assert vector.value_at_date(date(2026, 1, 21)) == 160.0


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
    vector_csv_path = tmp_path / "vector.csv"

    assert vector.interpolate_at(5) == 110.0
    assert resampled.simulation_days == (0.0, 5.0, 10.0, 15.0, 20.0)
    assert resampled.values == (100.0, 110.0, 120.0, 140.0, 160.0)
    assert vector.statistics() == {
        "COUNT": 3,
        "MIN": 100.0,
        "MAX": 160.0,
        "FIRST": 100.0,
        "LAST": 160.0,
    }
    assert vector.rows()[1] == {
        "KEY": "FOPR",
        "DATE": "2026-01-11",
        "REPORT_STEP": 1,
        "SIMULATION_DAYS": 10.0,
        "VALUE": 120.0,
        "UNIT": "SM3/DAY",
    }
    vector.to_csv(vector_csv_path)
    assert "KEY,DATE,REPORT_STEP,SIMULATION_DAYS,VALUE,UNIT" in (
        vector_csv_path.read_text(encoding="utf-8")
    )

    dataset.to_csv(csv_path, keys=["FOPR", "FOPT"])
    rows = dataset.rows(keys=["FOPR"])
    csv_text = csv_path.read_text(encoding="utf-8")
    assert rows == (
        {
            "DATE": "2026-01-01",
            "REPORT_STEP": 0,
            "SIMULATION_DAYS": 0.0,
            "FOPR": 100.0,
        },
        {
            "DATE": "2026-01-11",
            "REPORT_STEP": 1,
            "SIMULATION_DAYS": 10.0,
            "FOPR": 120.0,
        },
        {
            "DATE": "2026-01-21",
            "REPORT_STEP": 2,
            "SIMULATION_DAYS": 20.0,
            "FOPR": 160.0,
        },
    )
    assert "DATE,REPORT_STEP,SIMULATION_DAYS,FOPR,FOPT" in csv_text
    assert "2026-01-11,1,10.0,120.0,1000.0" in csv_text
    assert dataset.time_axis_rows()[1] == {
        "TIME_INDEX": 1,
        "DATE": "2026-01-11",
        "REPORT_STEP": 1,
        "SIMULATION_DAYS": 10.0,
    }
    assert dataset.vector_metadata_rows()[0] == {
        "KEY": "FOPR",
        "KEYWORD": "FOPR",
        "QUALIFIER": None,
        "QUALIFIER_KIND": None,
        "UNIT": "SM3/DAY",
        "CLASSIFICATION": "field",
        "LOADED": True,
    }
    selected = dataset.select_by_filter(pattern="WO*", qualifier_kind="well")
    assert selected.keys() == ("WOPR:PROD-1",)
    time_axis_csv_path = tmp_path / "summary_time_axis.csv"
    metadata_csv_path = tmp_path / "summary_vectors.csv"
    dataset.time_axis_to_csv(time_axis_csv_path)
    dataset.vector_metadata_to_csv(metadata_csv_path)
    assert "TIME_INDEX,DATE,REPORT_STEP,SIMULATION_DAYS" in (
        time_axis_csv_path.read_text(encoding="utf-8")
    )
    assert "KEY,KEYWORD,QUALIFIER,QUALIFIER_KIND,UNIT,CLASSIFICATION,LOADED" in (
        metadata_csv_path.read_text(encoding="utf-8")
    )

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


def test_public_summary_facade_loads_explicit_summary_paths(tmp_path: Path) -> None:
    metadata_path = tmp_path / "meta.txt"
    data_path = tmp_path / "data.txt"
    metadata_path.write_text(_metadata_text(), encoding="utf-8")
    data_path.write_text(_unified_data_text(), encoding="utf-8")

    dataset = load_summary_from_paths(metadata_path, (data_path,))

    assert dataset.keys() == ("FOPR", "FOPT", "WOPR:PROD-1")
    assert dataset.unified is True
    assert dataset.vector("FOPT").values == (0.0, 1000.0, 2400.0)


def test_public_summary_facade_loads_explicit_non_unified_paths(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "meta.txt"
    first_data_path = tmp_path / "first.txt"
    second_data_path = tmp_path / "second.txt"
    metadata_path.write_text("VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /", encoding="utf-8")
    first_data_path.write_text(
        "TIME 10 / DATES '2026-01-11' / VALUES 'FOPR' 120 /",
        encoding="utf-8",
    )
    second_data_path.write_text(
        "TIME 20 / DATES '2026-01-21' / VALUES 'FOPR' 160 /",
        encoding="utf-8",
    )

    dataset = load_summary_from_paths(
        metadata_path,
        (first_data_path, second_data_path),
        report_steps=(1, 2),
    )

    assert dataset.unified is False
    assert dataset.report_steps == (1, 2)
    assert dataset.vector("FOPR").values == (120.0, 160.0)


def test_explicit_summary_paths_validate_report_step_count(tmp_path: Path) -> None:
    metadata_path = tmp_path / "meta.txt"
    data_path = tmp_path / "data.txt"
    metadata_path.write_text("VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /", encoding="utf-8")
    data_path.write_text(_unified_data_text(), encoding="utf-8")

    with pytest.raises(ValueError, match="report_steps"):
        load_summary_from_paths(metadata_path, (data_path,), report_steps=(1, 2))


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
