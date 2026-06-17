import csv
from pathlib import Path

from reservoir_data.application.export_service import ExportService
from reservoir_data.domain.keyword.keyword_record import KeywordRecord
from reservoir_data.formats.grdecl.reader import GrdeclReader
from reservoir_data.formats.grdecl.writer import GrdeclWriter
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.init.init_reader import InitReader
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.export import (
    PropertyExportLayout,
    PropertyExportOptions,
    PropertyTableExportOptions,
)


def _minimal_grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def test_grdecl_writer_formats_supported_value_types() -> None:
    record = KeywordRecord.from_values(
        "mixed",
        ("A'B", True, False, None, 3, 1.25),
    )

    text = GrdeclWriter(values_per_line=3).format_records((record,))
    dataset = GrdeclReader().parser.parse_text(text)

    assert "'A''B'" in text
    assert dataset.record("MIXED").values == ("A'B", True, False, None, 3, 1.25)


def test_export_service_round_trips_grid_geometry(tmp_path: Path) -> None:
    source_path = tmp_path / "CASE.EGRID"
    export_path = tmp_path / "EXPORTED.GRDECL"
    source_path.write_text(_minimal_grid_text(), encoding="utf-8")
    grid = GridReader().read(source_path)

    ExportService().write_grid_grdecl(grid, export_path)
    reloaded = GridReader().read(export_path)

    assert reloaded.dimensions == grid.dimensions
    assert reloaded.geometry.export_coord() == grid.geometry.export_coord()
    assert reloaded.geometry.export_zcorn() == grid.geometry.export_zcorn()
    assert reloaded.active_cell_map.activity_mask == grid.active_cell_map.activity_mask


def test_export_service_exports_grid_cell_rows_and_csv(tmp_path: Path) -> None:
    source_path = tmp_path / "CASE.EGRID"
    csv_path = tmp_path / "GRID.csv"
    source_path.write_text(_minimal_grid_text(), encoding="utf-8")
    grid = GridReader().read(source_path)

    service = ExportService()
    rows = service.grid_cell_rows(grid)
    service.write_grid_cell_csv(grid, csv_path)
    csv_rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))

    assert len(rows) == 2
    assert rows[0]["i"] == 0
    assert rows[0]["simulator_i"] == 1
    assert rows[0]["global_index"] == 0
    assert rows[0]["active_index"] == 0
    assert rows[0]["is_active"] is True
    assert rows[0]["top"] == 100.0
    assert rows[0]["bottom"] == 110.0
    assert rows[0]["thickness"] == 10.0
    assert rows[1]["active_index"] is None
    assert rows[1]["simulator_global_index"] == 2
    assert csv_rows[1]["is_active"] == "False"
    assert csv_rows[1]["active_index"] == ""


def test_export_service_exports_properties_in_requested_layout(
    tmp_path: Path,
) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.FINIT"
    export_path = tmp_path / "PROPS.GRDECL"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text(
        """
        PORO 0.25 /
        PRESSURE 100 200 /
        """,
        encoding="utf-8",
    )
    grid = GridReader().read(grid_path)
    properties = InitReader().read(
        init_path,
        grid=grid,
        names=("PORO", "PRESSURE"),
    )

    ExportService().write_properties_grdecl(
        properties,
        export_path,
        names=("PORO", "PRESSURE"),
        options=PropertyExportOptions(
            target_layout=PropertyExportLayout.GLOBAL,
            inactive_default=0.0,
        ),
    )
    dataset = GrdeclReader().read(export_path)

    assert dataset.record("PORO").values == (0.25, 0.0)
    assert dataset.record("PRESSURE").values == (100, 200)


def test_export_service_exports_property_table_rows_and_csv(tmp_path: Path) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.FINIT"
    csv_path = tmp_path / "PROPS.csv"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text(
        """
        PORO 0.25 /
        PRESSURE 100 200 /
        """,
        encoding="utf-8",
    )
    grid = GridReader().read(grid_path)
    properties = InitReader().read(
        init_path,
        grid=grid,
        names=("PORO", "PRESSURE"),
    )

    service = ExportService()
    poro_rows = service.property_rows(
        properties.property("PORO"),
        options=PropertyTableExportOptions(
            target_layout=PropertyExportLayout.GLOBAL,
            inactive_default=0.0,
        ),
    )
    pressure_rows = service.property_rows(
        properties.property("PRESSURE"),
        options=PropertyTableExportOptions(
            target_layout=PropertyExportLayout.ACTIVE,
        ),
    )
    service.write_properties_csv(
        properties,
        csv_path,
        names=("PORO",),
        options=PropertyTableExportOptions(inactive_default=0.0),
    )
    csv_rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))

    assert [row["value"] for row in poro_rows] == [0.25, 0.0]
    assert poro_rows[1]["active_index"] is None
    assert [row["value"] for row in pressure_rows] == [100]
    assert pressure_rows[0]["property"] == "PRESSURE"
    assert [row["value"] for row in csv_rows] == ["0.25", "0.0"]


def test_public_case_exports_grid_and_selected_properties(tmp_path: Path) -> None:
    grid_path = tmp_path / "CASE.FEGRID"
    init_path = tmp_path / "CASE.FINIT"
    exported_grid = tmp_path / "CASE_EXPORT.GRDECL"
    exported_props = tmp_path / "CASE_PROPS.GRDECL"
    exported_grid_csv = tmp_path / "CASE_GRID.csv"
    exported_props_csv = tmp_path / "CASE_PROPS.csv"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text("PORO 0.30 / PRESSURE 10 20 /", encoding="utf-8")

    case = SimulationCase.open(tmp_path / "CASE")
    case.export_grid_grdecl(exported_grid)
    case.export_grid_cell_csv(exported_grid_csv)
    case.export_properties_grdecl(
        exported_props,
        names=("PORO",),
        options=PropertyExportOptions(
            target_layout=PropertyExportLayout.GLOBAL,
            inactive_default=0.0,
        ),
    )
    case.export_properties_csv(
        exported_props_csv,
        names=("PORO",),
        options=PropertyTableExportOptions(inactive_default=0.0),
    )

    assert GridReader().read(exported_grid).total_cell_count == 2
    assert GrdeclReader().read(exported_props).record("PORO").values == (0.3, 0.0)
    assert len(list(csv.DictReader(exported_grid_csv.open(encoding="utf-8")))) == 2
    assert [
        row["value"]
        for row in csv.DictReader(exported_props_csv.open(encoding="utf-8"))
    ] == ["0.3", "0.0"]
