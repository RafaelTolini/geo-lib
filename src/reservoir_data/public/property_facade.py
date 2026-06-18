"""Public property facade exports."""

from reservoir_data.domain.property.grid_property import GridProperty, PropertyLayout
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.schemas.export import (
    PropertyExportLayout,
    PropertyExportOptions,
    PropertyTableExportOptions,
)


def load_properties_from_path(
    path,
    grid=None,
    names=None,
    lazy: bool = True,
) -> PropertyCollection:
    """Load supported formatted initialization properties from a path."""

    from reservoir_data.application.grid_property_service import GridPropertyService

    return GridPropertyService().load_properties_from_path(
        path,
        grid=grid,
        names=names,
        lazy=lazy,
    )


__all__ = [
    "GridProperty",
    "PropertyCollection",
    "PropertyExportLayout",
    "PropertyExportOptions",
    "PropertyLayout",
    "PropertyTableExportOptions",
    "load_properties_from_path",
]
