from datetime import date
from pathlib import Path

import pytest

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import InvalidReportStepError, ParseError
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.restart.formatted_restart_reader import (
    FormattedRestartReader,
)
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.detection import FormatDetectionResult


def _grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def _formatted_restart_detection(
    path: Path,
    unified: bool = True,
    report_step: int | None = None,
) -> FormatDetectionResult:
    return FormatDetectionResult(
        path=path,
        file_category=FileCategory.RESTART,
        formatted=True,
        unified=unified,
        report_step=report_step,
        confidence=1.0,
        diagnostics=("test fixture",),
    )


def test_formatted_restart_reader_indexes_unified_reports_lazily(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CASE.FUNRST"
    path.write_text(
        """
        REPORT 1 10.0 '2026-01-10' /
        PRESSURE 100 200 /
        SWAT 0.1 0.2 /
        REPORT 2 20.0 '2026-01-20' /
        PRESSURE 300 400 /
        """,
        encoding="utf-8",
    )

    dataset = FormattedRestartReader().read(
        path,
        detection=_formatted_restart_detection(path),
    )

    assert dataset.unified is True
    assert dataset.report_steps() == (1, 2)
    assert dataset.headers()[0].simulation_days == 10.0
    assert dataset.headers()[0].report_date == date(2026, 1, 10)

    report = dataset.report_by_step(2)
    assert not report.is_payload_loaded
    assert report.keywords.names() == ("PRESSURE",)
    assert report.is_payload_loaded


def test_restart_dataset_queries_and_grid_property_mapping(tmp_path: Path) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    restart_path = tmp_path / "CASE.FUNRST"
    grid_path.write_text(_grid_text(), encoding="utf-8")
    restart_path.write_text(
        """
        REPORT 3 30.0 '2026-02-01' /
        PRESSURE 1000 2000 /
        ACTIVEPRESS 700 /
        """,
        encoding="utf-8",
    )
    grid = GridReader().read(grid_path)
    dataset = FormattedRestartReader().read(
        restart_path,
        detection=_formatted_restart_detection(restart_path),
    ).with_grid(grid)

    report = dataset.report_by_index(0)
    pressure = report.property("PRESSURE")
    active_pressure = report.property("ACTIVEPRESS")

    assert dataset.report_by_simulation_days(30.0) is report
    assert dataset.report_by_date(date(2026, 2, 1)) is report
    assert pressure.to_active_array() == (1000,)
    assert pressure.value_at(CellIndex.ijk(1, 0, 0)) == 2000
    assert active_pressure.to_global_array(default_value=0) == (700, 0)

    with pytest.raises(InvalidReportStepError):
        dataset.report_by_step(99)


def test_public_case_loads_formatted_unified_restarts(tmp_path: Path) -> None:
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
    dataset = case.load_restarts()

    assert dataset.report_steps() == (1, 2)
    assert dataset.report_by_step(1).property("PRESSURE").values == (10,)


def test_public_case_groups_formatted_non_unified_restarts(tmp_path: Path) -> None:
    (tmp_path / "CASE.F0002").write_text("PRESSURE 200 /", encoding="utf-8")
    (tmp_path / "CASE.F0001").write_text("PRESSURE 100 /", encoding="utf-8")

    dataset = SimulationCase.open(tmp_path / "CASE").load_restarts()

    assert dataset.unified is False
    assert dataset.report_steps() == (1, 2)
    assert dataset.report_by_step(2).property("PRESSURE").values == (200,)


def test_formatted_restart_reader_reports_corrupt_blocks(tmp_path: Path) -> None:
    path = tmp_path / "CASE.FUNRST"
    reader = FormattedRestartReader()

    path.write_text("PRESSURE 1 /", encoding="utf-8")
    with pytest.raises(ParseError, match="REPORT"):
        reader.read(path, detection=_formatted_restart_detection(path))

    path.write_text(
        "REPORT 1 2 '2026-01-01' / REPORT 2 3 '2026-01-02'",
        encoding="utf-8",
    )
    with pytest.raises(ParseError, match="Unterminated"):
        reader.read(path, detection=_formatted_restart_detection(path))

    path.write_bytes(b"\x04\x00\x00\x00ABCD\x04\x00\x00\x00")
    with pytest.raises(ParseError, match="binary-looking"):
        reader.read(path, detection=_formatted_restart_detection(path))


def test_non_unified_report_step_mismatch_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "CASE.F0007"
    path.write_text("REPORT 8 / PRESSURE 1 /", encoding="utf-8")

    with pytest.raises(ParseError, match="does not match"):
        FormattedRestartReader().read(
            path,
            detection=_formatted_restart_detection(
                path,
                unified=False,
                report_step=7,
            ),
        )
