from pathlib import Path

import pytest

from reservoir_data.exceptions.errors import (
    InvalidReportStepError,
    MissingKeywordError,
    UnsupportedFormatError,
)
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.loading import (
    GeometryValidationLevel,
    GridLoadOptions,
    RestartLoadOptions,
    SummaryLoadOptions,
)


def _grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def _write_summary_fixture(path: Path) -> None:
    (path / "CASE.FSMSPEC").write_text(
        """
        VECTOR 'FOPR' 'SM3/DAY' 'FIELD' /
        VECTOR 'FOPT' 'SM3' 'FIELD' /
        """,
        encoding="utf-8",
    )
    (path / "CASE.FUNSMRY").write_text(
        """
        TIME 0 10 /
        DATES '2026-01-01' '2026-01-11' /
        REPORTS 0 1 /
        VALUES 'FOPR' 100 120 /
        VALUES 'FOPT' 0 1000 /
        """,
        encoding="utf-8",
    )


def test_grid_load_options_validate_supported_and_unsupported_flags(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.EGRID").write_text(_grid_text(), encoding="utf-8")
    case = SimulationCase.open(tmp_path / "CASE")

    grid = case.load_grid(
        options=GridLoadOptions(
            validate_geometry_level=GeometryValidationLevel.BASIC,
        )
    )

    assert grid.total_cell_count == 2
    with pytest.raises(UnsupportedFormatError, match="Local grid"):
        case.load_grid(options=GridLoadOptions(load_local_grids=True))
    with pytest.raises(UnsupportedFormatError, match="Full corner-point"):
        case.load_grid(
            options=GridLoadOptions(
                validate_geometry_level=GeometryValidationLevel.FULL,
            )
        )


def test_restart_load_options_filter_reports_and_control_lazy_payloads(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.FUNRST").write_text(
        """
        REPORT 1 1.0 '2026-01-01' /
        PRESSURE 10 /
        REPORT 2 2.0 '2026-01-02' /
        PRESSURE 20 /
        """,
        encoding="utf-8",
    )
    case = SimulationCase.open(tmp_path / "CASE")

    dataset = case.load_restarts(
        options=RestartLoadOptions(
            requested_report_steps=(2,),
            lazy_keyword_arrays=False,
        )
    )

    assert dataset.report_steps() == (2,)
    assert dataset.report_by_step(2).is_payload_loaded
    assert dataset.report_by_step(2).property("PRESSURE").values == (20,)
    with pytest.raises(InvalidReportStepError, match="99"):
        case.load_restarts(
            options=RestartLoadOptions(requested_report_steps=(99,))
        )
    with pytest.raises(UnsupportedFormatError, match="load_wells"):
        case.load_restarts(options=RestartLoadOptions(load_well_data=True))


def test_summary_load_options_filter_vectors_and_control_lazy_values(
    tmp_path: Path,
) -> None:
    _write_summary_fixture(tmp_path)
    case = SimulationCase.open(tmp_path / "CASE")

    dataset = case.load_summary(
        options=SummaryLoadOptions(
            vector_filter=("FOPR",),
            lazy_vectors=False,
        )
    )

    assert dataset.keys() == ("FOPR",)
    assert dataset.is_vector_loaded("FOPR")
    assert dataset.vector("FOPR").values == (100.0, 120.0)
    with pytest.raises(MissingKeywordError):
        dataset.vector("FOPT")
    with pytest.raises(UnsupportedFormatError, match="restart metadata"):
        case.load_summary(
            options=SummaryLoadOptions(include_restart_metadata=True)
        )
