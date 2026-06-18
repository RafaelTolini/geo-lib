from pathlib import Path

import pytest

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.property.grid_property import PropertyLayout
from reservoir_data.exceptions.errors import (
    InvalidCellIndexError,
    MissingKeywordError,
    ParseError,
    PropertyShapeError,
)
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.init.init_reader import InitReader
from reservoir_data.public import load_grid_from_path as public_load_grid_from_path
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.public.grid_facade import load_grid_from_path
from reservoir_data.public.property_facade import load_properties_from_path


def _minimal_grid_text() -> str:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    return f"""
    SPECGRID 2 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    ACTNUM 1 0 /
    """


def test_grid_reader_loads_minimal_formatted_egrid_file(tmp_path: Path) -> None:
    path = tmp_path / "CASE.EGRID"
    path.write_text(_minimal_grid_text(), encoding="utf-8")

    grid = GridReader().read(path)

    assert grid.dimensions.nx == 2
    assert grid.dimensions.ny == 1
    assert grid.dimensions.nz == 1
    assert grid.total_cell_count == 2
    assert grid.active_cell_count == 1
    assert grid.cell(CellIndex.ijk(1, 0, 0)).is_active is False


def test_grid_reader_rejects_binary_like_grid_payload(tmp_path: Path) -> None:
    path = tmp_path / "CASE.EGRID"
    path.write_bytes(b"\x04\x00\x00\x00ABCD\x04\x00\x00\x00")

    with pytest.raises(ParseError, match="binary-looking"):
        GridReader().read(path)


def test_init_reader_loads_selected_properties_and_associates_grid(
    tmp_path: Path,
) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.INIT"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text(
        """
        PORO 0.25 /
        PRESSURE 100 200 /
        PERMX 10 20 /
        """,
        encoding="utf-8",
    )
    grid = GridReader().read(grid_path)

    properties = InitReader().read(init_path, grid=grid, names=["PORO", "PRESSURE"])

    assert properties.names() == ("PORO", "PRESSURE")
    assert not properties.has_property("PERMX")

    poro = properties.property("PORO")
    pressure = properties.property("PRESSURE")
    assert poro is not None
    assert pressure is not None
    assert poro.layout is PropertyLayout.ACTIVE
    assert pressure.layout is PropertyLayout.GLOBAL
    assert poro.to_global_array(default_value=0.0) == (0.25, 0.0)
    assert pressure.to_active_array() == (100,)
    assert pressure.value_at(CellIndex.ijk(1, 0, 0)) == 200

    with pytest.raises(InvalidCellIndexError):
        poro.value_at(CellIndex.ijk(1, 0, 0))


def test_init_reader_reports_missing_and_shape_mismatched_properties(
    tmp_path: Path,
) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.INIT"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text("BAD 1 2 3 /", encoding="utf-8")
    grid = GridReader().read(grid_path)

    with pytest.raises(MissingKeywordError):
        InitReader().read(init_path, grid=grid, names=["PORO"])

    with pytest.raises(PropertyShapeError, match="does not match"):
        InitReader().read(init_path, grid=grid)


def test_public_case_facade_loads_supported_grid_and_properties(
    tmp_path: Path,
) -> None:
    (tmp_path / "CASE.EGRID").write_text(_minimal_grid_text(), encoding="utf-8")
    (tmp_path / "CASE.INIT").write_text("PORO 0.3 / PRESSURE 10 20 /", encoding="utf-8")

    case = SimulationCase.open(tmp_path / "CASE")
    grid = case.load_grid()
    properties = case.load_properties(names=["PORO"])

    assert grid.active_cell_count == 1
    assert properties.names() == ("PORO",)
    poro = properties.property("PORO")
    assert poro is not None
    assert poro.to_global_array(default_value=0.0) == (0.3, 0.0)


def test_public_facades_load_explicit_grid_and_property_paths(
    tmp_path: Path,
) -> None:
    grid_path = tmp_path / "grid.txt"
    init_path = tmp_path / "init.txt"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text("PORO 0.25 / PRESSURE 10 20 /", encoding="utf-8")

    grid = load_grid_from_path(grid_path)
    root_grid = public_load_grid_from_path(grid_path)
    properties = load_properties_from_path(
        init_path,
        grid=grid,
        names=["PORO"],
        lazy=False,
    )

    assert grid.dimensions == root_grid.dimensions
    assert properties.names() == ("PORO",)
    assert properties.property("PORO").to_global_array(default_value=0.0) == (
        0.25,
        0.0,
    )


def test_property_collection_materializes_selected_lazy_properties(
    tmp_path: Path,
) -> None:
    grid_path = tmp_path / "CASE.EGRID"
    init_path = tmp_path / "CASE.INIT"
    grid_path.write_text(_minimal_grid_text(), encoding="utf-8")
    init_path.write_text("PORO 0.25 / PRESSURE 10 20 /", encoding="utf-8")
    grid = GridReader().read(grid_path)

    properties = InitReader().read(init_path, grid=grid, lazy=True)

    assert properties.names() == ("PORO", "PRESSURE")
    assert not properties.is_property_loaded("PORO")

    materialized = properties.materialize(["PORO"])

    assert materialized.names() == ("PORO",)
    assert materialized.is_property_loaded("PORO")
    assert materialized.property("PORO").to_active_array() == (0.25,)
    assert properties.is_property_loaded("PORO")
