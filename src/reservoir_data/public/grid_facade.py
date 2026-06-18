"""Public grid facade exports."""

from reservoir_data.domain.grid import (
    ActiveCellMap,
    CellIndex,
    GridCell,
    GridDimensions,
    GridGeometry,
    ReservoirGrid,
)
from reservoir_data.schemas.export import GridTableExportOptions
from reservoir_data.schemas.loading import GridLoadOptions


def load_grid_from_path(path, options: GridLoadOptions | None = None) -> ReservoirGrid:
    """Load a supported formatted grid from an explicit path."""

    from reservoir_data.application.grid_property_service import GridPropertyService

    return GridPropertyService().load_grid_from_path(path, options=options)


__all__ = [
    "ActiveCellMap",
    "CellIndex",
    "GridCell",
    "GridDimensions",
    "GridGeometry",
    "GridLoadOptions",
    "GridTableExportOptions",
    "ReservoirGrid",
    "load_grid_from_path",
]
