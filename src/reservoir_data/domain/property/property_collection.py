"""Collection of grid properties."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.exceptions.errors import MissingKeywordError


@dataclass(frozen=True, slots=True)
class PropertyCollection:
    """Ordered collection of grid properties."""

    properties: tuple[GridProperty, ...] = ()
    source: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "properties", tuple(self.properties))

    def __iter__(self) -> Iterator[GridProperty]:
        return iter(self.properties)

    def __len__(self) -> int:
        return len(self.properties)

    def names(self) -> tuple[str, ...]:
        """Return property names in order."""

        return tuple(property_.name for property_ in self.properties)

    def has_property(self, name: str) -> bool:
        """Return whether a property exists."""

        normalized_name = name.strip().upper()
        return any(property_.name == normalized_name for property_ in self.properties)

    def property(self, name: str, required: bool = True) -> GridProperty | None:
        """Return a property by name."""

        normalized_name = name.strip().upper()
        for property_ in self.properties:
            if property_.name == normalized_name:
                return property_
        if required:
            raise MissingKeywordError(f"Property {name!r} was not found")
        return None

    def with_grid(self, grid: ReservoirGrid) -> "PropertyCollection":
        """Return a collection with all properties associated with a grid."""

        return PropertyCollection(
            properties=tuple(property_.with_grid(grid) for property_ in self.properties),
            source=self.source,
        )
