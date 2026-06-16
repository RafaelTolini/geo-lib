import pytest

from reservoir_data.domain.grid.active_cell_map import ActiveCellMap
from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.grid.grid_dimensions import GridDimensions
from reservoir_data.domain.grid.grid_geometry import GridGeometry
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.exceptions.errors import (
    GridGeometryError,
    InvalidCellIndexError,
    PropertyShapeError,
)


def _geometry(dimensions: GridDimensions) -> GridGeometry:
    coord = tuple(float(index) for index in range(6 * dimensions.pillar_count))
    zcorn_values: list[float] = []
    for global_index in range(dimensions.total_cells):
        top = float(100 + 10 * global_index)
        bottom = top + 5.0
        zcorn_values.extend([top, top, top, top, bottom, bottom, bottom, bottom])
    return GridGeometry.from_sequences(dimensions, coord, tuple(zcorn_values))


def test_grid_dimensions_convert_between_ijk_and_global_index() -> None:
    dimensions = GridDimensions(nx=3, ny=2, nz=2)

    assert dimensions.total_cells == 12
    assert dimensions.global_index(2, 1, 1) == 11
    assert dimensions.ijk_from_global(4) == (1, 1, 0)
    assert dimensions.contains_ijk(0, 0, 0)
    assert not dimensions.contains_ijk(3, 0, 0)

    with pytest.raises(InvalidCellIndexError):
        dimensions.global_index(3, 0, 0)

    with pytest.raises(ValueError):
        GridDimensions(nx=0, ny=1, nz=1)


def test_cell_index_normalizes_zero_based_and_simulator_one_based_addresses() -> None:
    assert CellIndex.ijk(1, 2, 3).zero_based_ijk() == (1, 2, 3)
    assert CellIndex.ijk(1, 2, 3, simulator_one_based=True).zero_based_ijk() == (
        0,
        1,
        2,
    )
    assert CellIndex.ijk(0, 1, 2).simulator_ijk() == (1, 2, 3)
    assert CellIndex.global_cell(4, simulator_one_based=True).global_index == 3
    assert CellIndex.active_cell(2, simulator_one_based=True).active_index == 1

    with pytest.raises(ValueError):
        CellIndex(i=0, global_index=1)

    with pytest.raises(ValueError):
        CellIndex.ijk(0, 1, 1, simulator_one_based=True)


def test_active_cell_map_converts_plain_sequences() -> None:
    active_map = ActiveCellMap.from_activity_values([1, 0, 1, 0, 1], 5)

    assert active_map.active_cell_count == 3
    assert active_map.active_to_global == (0, 2, 4)
    assert active_map.global_to_active == (0, None, 1, None, 2)
    assert active_map.to_global([10, 20, 30], default_value=-1) == (
        10,
        -1,
        20,
        -1,
        30,
    )
    assert active_map.compress_global([1, 2, 3, 4, 5]) == (1, 3, 5)

    with pytest.raises(PropertyShapeError):
        active_map.to_global([1, 2])

    with pytest.raises(PropertyShapeError):
        active_map.compress_global([1, 2])


def test_active_cell_map_converts_numpy_arrays_when_available() -> None:
    numpy = pytest.importorskip("numpy")
    active_map = ActiveCellMap.from_activity_values([1, 0, 1, 0], 4)

    global_values = active_map.to_global(numpy.array([1.5, 2.5]), default_value=0.0)
    active_values = active_map.compress_global(numpy.array([9, 8, 7, 6]))

    assert global_values.tolist() == [1.5, 0.0, 2.5, 0.0]
    assert active_values.tolist() == [9, 7]


def test_reservoir_grid_resolves_cells_and_geometry_values() -> None:
    dimensions = GridDimensions(nx=2, ny=2, nz=1)
    grid = ReservoirGrid(
        dimensions=dimensions,
        geometry=_geometry(dimensions),
        active_cell_map=ActiveCellMap.from_activity_values([1, 0, 1, 1], 4),
    )

    inactive = grid.cell(CellIndex.ijk(1, 0, 0))
    active = grid.cell(CellIndex.active_cell(1))

    assert grid.total_cell_count == 4
    assert grid.active_cell_count == 3
    assert inactive.global_index == 1
    assert inactive.active_index is None
    assert not inactive.is_active
    assert active.global_index == 2
    assert active.ijk == (0, 1, 0)
    assert active.simulator_ijk == (1, 2, 1)
    assert active.top == 120.0
    assert active.bottom == 125.0
    assert active.depth == 122.5
    assert active.thickness == 5.0
    assert active.center == (0.5, 1.5, 122.5)

    with pytest.raises(InvalidCellIndexError):
        grid.cell(CellIndex.global_cell(4))

    with pytest.raises(GridGeometryError):
        active.volume


def test_grid_geometry_validates_array_lengths() -> None:
    dimensions = GridDimensions(nx=1, ny=1, nz=1)

    with pytest.raises(GridGeometryError, match="COORD"):
        GridGeometry.from_sequences(dimensions, [0.0], [0.0] * 8)

    with pytest.raises(GridGeometryError, match="ZCORN"):
        GridGeometry.from_sequences(dimensions, [0.0] * 24, [0.0])

    with pytest.raises(GridGeometryError, match="MAPAXES"):
        GridGeometry.from_sequences(dimensions, [0.0] * 24, [0.0] * 8, [0.0])
