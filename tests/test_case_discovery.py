from pathlib import Path

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import (
    FileDetectionError,
    FileReadError,
    GridGeometryError,
    UnsupportedFormatError,
)
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.loading import LoadCaseOptions


def _touch(directory: Path, *filenames: str) -> None:
    for filename in filenames:
        (directory / filename).write_text("", encoding="utf-8")


def test_simulation_case_open_discovers_files_by_basename(tmp_path: Path) -> None:
    _touch(
        tmp_path,
        "CASE.DATA",
        "CASE.EGRID",
        "CASE.INIT",
        "CASE.UNRST",
        "CASE.X0007",
        "CASE.SMSPEC",
        "CASE.UNSMRY",
        "OTHER.DATA",
    )

    case = SimulationCase.open(tmp_path / "CASE")

    assert case.case_name == "CASE"
    assert case.root_path == tmp_path
    assert set(case.available_data()) == {
        FileCategory.DECK,
        FileCategory.GRID,
        FileCategory.INIT,
        FileCategory.RESTART,
        FileCategory.SUMMARY_METADATA,
        FileCategory.SUMMARY_DATA,
    }
    assert [item.path.name for item in case.files_for(FileCategory.RESTART)] == [
        "CASE.UNRST",
        "CASE.X0007",
    ]
    assert case.manifest.preferred_file(FileCategory.RESTART).path.name == "CASE.UNRST"


def test_simulation_case_open_respects_category_filter(tmp_path: Path) -> None:
    _touch(tmp_path, "CASE.DATA", "CASE.EGRID", "CASE.UNRST")

    case = SimulationCase.open(
        tmp_path / "CASE",
        LoadCaseOptions(file_categories=[FileCategory.GRID]),
    )

    assert case.available_data() == (FileCategory.GRID,)
    assert case.has_data(FileCategory.GRID)
    assert not case.has_data(FileCategory.DECK)


def test_opening_ambiguous_directory_raises_in_strict_mode(tmp_path: Path) -> None:
    _touch(tmp_path, "CASE_A.DATA", "CASE_B.DATA")

    with pytest.raises(FileDetectionError):
        SimulationCase.open(tmp_path)


def test_opening_missing_basename_raises_file_read_error(tmp_path: Path) -> None:
    with pytest.raises(FileReadError):
        SimulationCase.open(tmp_path / "MISSING")


def test_grid_loader_reports_malformed_grid_files(tmp_path: Path) -> None:
    _touch(tmp_path, "CASE.EGRID")

    case = SimulationCase.open(tmp_path / "CASE")

    with pytest.raises(GridGeometryError, match="SPECGRID"):
        case.load_grid()


def test_loader_reports_missing_grid_category(
    tmp_path: Path,
) -> None:
    _touch(tmp_path, "CASE.DATA")

    case = SimulationCase.open(tmp_path / "CASE")

    with pytest.raises(FileReadError, match="No grid files"):
        case.load_grid()


def test_restart_loader_remains_explicitly_unsupported(tmp_path: Path) -> None:
    _touch(tmp_path, "CASE.UNRST")

    case = SimulationCase.open(tmp_path / "CASE")

    with pytest.raises(UnsupportedFormatError, match="does not parse file payloads"):
        case.load_restarts()
