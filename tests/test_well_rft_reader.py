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
    rows = wells.rows()

    assert wells.names() == ("PROD-1",)
    assert wells.has_well("prod-1")
    assert wells.filter_names("prod*") == ("PROD-1",)
    assert wells.select(["prod-1"]).names() == ("PROD-1",)
    assert rows[0]["WELL"] == "PROD-1"
    assert rows[0]["REPORT_STEP"] == 1
    assert rows[0]["RATE_OIL"] == 120.0
    assert rows[0]["CONNECTION_COUNT"] == 1
    assert rows[0]["SEGMENT_COUNT"] == 1
    connection_rows = wells.connection_rows()
    segment_rows = wells.segment_rows()
    assert connection_rows[0]["WELL"] == "PROD-1"
    assert connection_rows[0]["REPORT_STEP"] == 1
    assert connection_rows[0]["SIMULATOR_I"] == 1
    assert connection_rows[0]["DIRECTION"] == "Z"
    assert connection_rows[0]["CONNECTION_FACTOR"] == 0.75
    assert segment_rows[0]["SEGMENT_ID"] == 1
    assert segment_rows[0]["DEPTH"] == 1500.0
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

    csv_path = tmp_path / "wells.csv"
    wells.to_csv(csv_path)
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "WELL,REPORT_STEP,SIMULATION_DAYS,DATE,WELL_TYPE,OPEN" in csv_text
    assert "RATE_OIL" in csv_text
    connections_csv_path = tmp_path / "well_connections.csv"
    segments_csv_path = tmp_path / "well_segments.csv"
    wells.connections_to_csv(connections_csv_path)
    wells.segments_to_csv(segments_csv_path)
    assert "CONNECTION_INDEX,I,J,K,SIMULATOR_I" in connections_csv_path.read_text(
        encoding="utf-8"
    )
    assert "SEGMENT_ID,PARENT_ID,DEPTH,LENGTH" in segments_csv_path.read_text(
        encoding="utf-8"
    )


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
    header_rows = dataset.header_rows()

    assert dataset.wells() == ("PROD-1",)
    assert dataset.record_types() == ("PLT", "RFT")
    assert len(dataset.records_for(well="prod-1")) == 2
    assert dataset.select(record_type="RFT").dates() == (date(2026, 2, 1),)
    assert header_rows[0]["WELL"] == "PROD-1"
    assert header_rows[0]["TYPE"] == "RFT"
    assert header_rows[0]["MEASUREMENTS_LOADED"] is False
    assert not rft_record.is_measurements_loaded
    rft_rows = rft_record.measurement_rows()
    assert rft_rows[0]["WELL"] == "PROD-1"
    assert rft_rows[0]["PRESSURE"] == 250.0
    assert rft_rows[0]["SATURATION_WATER"] == 0.20
    assert rft_record.is_measurements_loaded
    assert rft_record.measurements[0].pressure == 250.0
    assert rft_record.measurements[0].saturations["WATER"] == 0.20
    assert rft_record.measurements[0].cell.zero_based_ijk() == (0, 0, 0)
    assert rft_record.is_measurements_loaded
    assert plt_record.measurements[0].rates["OIL"] == 100.0
    assert plt_record.measurements[0].cell.zero_based_ijk() == (1, 0, 0)

    assert dataset.header_rows()[0]["MEASUREMENTS_LOADED"] is True
    measurement_rows = dataset.measurement_rows()
    assert len(measurement_rows) == 2
    assert measurement_rows[1]["RATE_OIL"] == 100.0
    csv_path = tmp_path / "rft_headers.csv"
    dataset.to_csv(csv_path)
    assert "WELL,DATE,TYPE,SOURCE,MEASUREMENTS_LOADED" in (
        csv_path.read_text(encoding="utf-8")
    )
    measurement_csv_path = tmp_path / "rft_measurements.csv"
    dataset.measurements_to_csv(measurement_csv_path)
    assert "MEASUREMENT_INDEX,I,J,K,SIMULATOR_I" in measurement_csv_path.read_text(
        encoding="utf-8"
    )


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
