from datetime import date
from pathlib import Path

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.exceptions.errors import (
    InvalidCellIndexError,
    ParseError,
    RftDataError,
    UnsupportedFormatError,
    WellDataError,
)
from reservoir_data.formats.rft.formatted_rft_reader import FormattedRftReader
from reservoir_data.public.case_facade import SimulationCase


def _grid_text(nx: int = 2) -> str:
    coord = " ".join(str(value) for value in range((nx + 1) * 2 * 6))
    z_values = []
    for cell in range(nx):
        top = 100 + cell * 10
        bottom = top + 5
        z_values.extend([top, top, top, top, bottom, bottom, bottom, bottom])
    zcorn = " ".join(str(value) for value in z_values)
    actnum = " ".join("1" for _ in range(nx))
    return f"""
    SPECGRID {nx} 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM {actnum} /
    """


def _restart_with_wells() -> str:
    return """
    REPORT 1 10.0 '2026-01-10' /
    WELL 'PROD-1' 'PRODUCER' 'OPEN' /
    WCONN 'PROD-1' 1 1 1 'OPEN' 'Z' 0.75 'MATRIX' /
    WRATE 'PROD-1' 'OIL' 120.0 /
    WRATE 'PROD-1' 'WATER' 12.0 /
    WSEG 'PROD-1' 1 0 1500.0 10.0 /
    REPORT 2 20.0 '2026-01-20' /
    WELL 'PROD-1' 'PRODUCER' 'SHUT' /
    WCONN 'PROD-1' 2 1 1 'SHUT' 'X' 0.50 'MATRIX' /
    WRATE 'PROD-1' 'OIL' 0.0 /
    """


def test_public_case_loads_well_timeline_from_formatted_restart(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.FEGRID").write_text(_grid_text(), encoding="utf-8")
    (tmp_path / "CASE.FUNRST").write_text(_restart_with_wells(), encoding="utf-8")

    wells = SimulationCase.open(tmp_path / "CASE").load_wells()
    timeline = wells.timeline("prod-1")
    first = timeline.at_report_step(1)
    second = timeline.at_date(date(2026, 1, 20))

    assert wells.names() == ("PROD-1",)
    assert timeline.report_steps() == (1, 2)
    assert first.well_type == "PRODUCER"
    assert first.is_open is True
    assert first.rate("oil") == 120.0
    assert first.connections[0].cell == CellIndex.ijk(1, 1, 1, simulator_one_based=True)
    assert first.connections[0].cell.zero_based_ijk() == (0, 0, 0)
    assert first.connections[0].direction == "Z"
    assert first.connections[0].connection_factor == 0.75
    assert first.segments[0].segment_id == 1
    assert second.is_open is False
    assert second.rate("OIL") == 0.0


def test_well_loading_can_skip_segments(tmp_path: Path) -> None:
    (tmp_path / "CASE.FUNRST").write_text(
        """
        REPORT 1 1.0 '2026-01-01' /
        WELL 'PROD-1' 'PRODUCER' 'OPEN' /
        WSEG 'PROD-1' 0 0 100.0 10.0 /
        """,
        encoding="utf-8",
    )
    case = SimulationCase.open(tmp_path / "CASE")

    wells = case.load_wells(load_segments=False)
    assert wells.timeline("PROD-1").at_report_step(1).segments == ()

    with pytest.raises(WellDataError, match="segment_id"):
        case.load_wells(load_segments=True)


def test_well_connection_cell_index_is_validated_when_grid_exists(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.FEGRID").write_text(_grid_text(nx=1), encoding="utf-8")
    (tmp_path / "CASE.FUNRST").write_text(
        """
        REPORT 1 1.0 '2026-01-01' /
        WELL 'PROD-1' 'PRODUCER' 'OPEN' /
        WCONN 'PROD-1' 2 1 1 'OPEN' /
        """,
        encoding="utf-8",
    )

    with pytest.raises(InvalidCellIndexError):
        SimulationCase.open(tmp_path / "CASE").load_wells()


def test_well_reader_reports_missing_well_records(tmp_path: Path) -> None:
    (tmp_path / "CASE.FUNRST").write_text(
        """
        REPORT 1 1.0 '2026-01-01' /
        PRESSURE 100 /
        """,
        encoding="utf-8",
    )

    with pytest.raises(WellDataError, match="WELL"):
        SimulationCase.open(tmp_path / "CASE").load_wells()


def test_public_case_loads_formatted_rft_and_plt(tmp_path: Path) -> None:
    (tmp_path / "CASE.FEGRID").write_text(_grid_text(), encoding="utf-8")
    (tmp_path / "CASE.FRFT").write_text(
        """
        RFTREC 'PROD-1' '2026-02-01' 'RFT' /
        RFTCELL 1 1 1 1500.0 250.0 0.20 0.70 0.10 /
        """,
        encoding="utf-8",
    )
    (tmp_path / "CASE.FPLT").write_text(
        """
        RFTREC 'PROD-1' '2026-02-02' 'PLT' /
        PLTCELL 2 1 1 1510.0 245.0 100.0 10.0 1.0 /
        """,
        encoding="utf-8",
    )

    dataset = SimulationCase.open(tmp_path / "CASE").load_rft()
    rft_record = dataset.record("prod-1", date(2026, 2, 1))
    plt_record = dataset.record("PROD-1", date(2026, 2, 2), record_type="PLT")

    assert dataset.wells() == ("PROD-1",)
    assert not rft_record.is_measurements_loaded
    assert rft_record.measurements[0].pressure == 250.0
    assert rft_record.measurements[0].saturations["WATER"] == 0.20
    assert rft_record.measurements[0].cell.zero_based_ijk() == (0, 0, 0)
    assert rft_record.is_measurements_loaded
    assert plt_record.measurements[0].rates["OIL"] == 100.0
    assert plt_record.measurements[0].cell.zero_based_ijk() == (1, 0, 0)


def test_rft_dataset_reports_unknown_and_malformed_records(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.FRFT").write_text(
        """
        RFTREC 'PROD-1' '2026-02-01' 'RFT' /
        RFTCELL 1 1 1 1500.0 250.0 /
        """,
        encoding="utf-8",
    )
    dataset = SimulationCase.open(tmp_path / "CASE").load_rft()

    with pytest.raises(RftDataError):
        dataset.record("NOPE", date(2026, 2, 1))

    (tmp_path / "BAD.FRFT").write_text(
        "RFTCELL 1 1 1 1500.0 250.0 /",
        encoding="utf-8",
    )
    bad_case = SimulationCase.open(tmp_path / "BAD")
    with pytest.raises(ParseError, match="RFTREC"):
        bad_case.load_rft()

    (tmp_path / "BINARY.FRFT").write_bytes(b"\x04\x00\x00\x00ABCD\x04\x00\x00\x00")
    binary_case = SimulationCase.open(tmp_path / "BINARY")
    binary_detection = binary_case.files_for(FileCategory.RFT)[0]
    with pytest.raises(ParseError, match="binary-looking"):
        FormattedRftReader().read((binary_detection,))


def test_unformatted_rft_loader_remains_explicitly_unsupported(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.RFT").write_text("", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError, match="formatted RFT/PLT"):
        SimulationCase.open(tmp_path / "CASE").load_rft()
