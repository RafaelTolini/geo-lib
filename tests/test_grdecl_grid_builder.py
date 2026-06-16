import pytest

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.exceptions.errors import GridGeometryError, PropertyShapeError
from reservoir_data.formats.grdecl.grid_builder import GrdeclGridBuilder


def test_grdecl_grid_builder_builds_minimal_grid_from_geometry_keywords() -> None:
    coord = " ".join(str(value) for value in range(36))
    zcorn = "100 100 100 100 110 110 110 110 200 200 200 200 220 220 220 220"
    text = f"""
    SPECGRID
      2 1 1 1 F /
    COORD
      {coord} /
    ZCORN
      {zcorn} /
    ACTNUM
      1 0 /
    """

    grid = GrdeclGridBuilder().build_from_text(text, source="minimal")

    assert grid.dimensions.nx == 2
    assert grid.dimensions.ny == 1
    assert grid.dimensions.nz == 1
    assert grid.total_cell_count == 2
    assert grid.active_cell_count == 1
    assert grid.geometry.export_coord() == tuple(float(value) for value in range(36))
    assert grid.cell(CellIndex.ijk(0, 0, 0)).depth == 105.0
    assert not grid.cell(CellIndex.ijk(1, 0, 0)).is_active


def test_grdecl_grid_builder_defaults_to_all_active_when_actnum_is_missing() -> None:
    coord = " ".join("0" for _ in range(24))
    zcorn = " ".join("1" for _ in range(8))
    text = f"""
    SPECGRID 1 1 1 1 F /
    COORD {coord} /
    ZCORN {zcorn} /
    """

    grid = GrdeclGridBuilder().build_from_text(text)

    assert grid.active_cell_count == 1
    assert grid.cell(CellIndex.global_cell(0)).is_active


def test_grdecl_grid_builder_reports_missing_and_mismatched_grid_keywords() -> None:
    builder = GrdeclGridBuilder()
    coord = " ".join("0" for _ in range(24))
    zcorn = " ".join("1" for _ in range(8))

    with pytest.raises(GridGeometryError, match="SPECGRID"):
        builder.build_from_text(f"COORD {coord} / ZCORN {zcorn} /")

    with pytest.raises(GridGeometryError, match="ZCORN"):
        builder.build_from_text(f"SPECGRID 1 1 1 1 F / COORD {coord} / ZCORN 1 /")

    with pytest.raises(PropertyShapeError, match="Activity mask"):
        builder.build_from_text(
            f"SPECGRID 1 1 1 1 F / COORD {coord} / ZCORN {zcorn} / ACTNUM 1 0 /"
        )
