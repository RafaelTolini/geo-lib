"""Collection of grid properties."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.exceptions.errors import MissingKeywordError


@dataclass(frozen=True, slots=True)
class PropertyCollection:
    """Ordered collection of grid properties."""

    properties: tuple[GridProperty, ...] = ()
    source: str | None = None
    property_loaders: Mapping[str, Callable[[], GridProperty]] = field(
        default_factory=dict
    )
    _loaded_properties: dict[str, GridProperty] = field(
        default_factory=dict,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        properties = tuple(self.properties)
        object.__setattr__(self, "properties", properties)
        normalized_loaders = {
            name.strip().upper(): loader
            for name, loader in self.property_loaders.items()
        }
        object.__setattr__(self, "property_loaders", normalized_loaders)
        object.__setattr__(
            self,
            "_loaded_properties",
            {property_.name: property_ for property_ in properties},
        )

    def __iter__(self) -> Iterator[GridProperty]:
        for name in self.names():
            property_ = self.property(name)
            if property_ is not None:
                yield property_

    def __len__(self) -> int:
        return len(self.names())

    def names(self) -> tuple[str, ...]:
        """Return property names in order."""

        eager_names = tuple(property_.name for property_ in self.properties)
        lazy_names = tuple(
            name for name in self.property_loaders if name not in eager_names
        )
        return (*eager_names, *lazy_names)

    def has_property(self, name: str) -> bool:
        """Return whether a property exists."""

        normalized_name = name.strip().upper()
        return any(property_.name == normalized_name for property_ in self.properties)

    def property(self, name: str, required: bool = True) -> GridProperty | None:
        """Return a property by name."""

        normalized_name = name.strip().upper()
        if normalized_name in self._loaded_properties:
            return self._loaded_properties[normalized_name]
        loader = self.property_loaders.get(normalized_name)
        if loader is not None:
            property_ = loader()
            self._loaded_properties[normalized_name] = property_
            return property_
        if required:
            raise MissingKeywordError(f"Property {name!r} was not found")
        return None

    def is_property_loaded(self, name: str) -> bool:
        """Return whether a lazy property has already been loaded."""

        return name.strip().upper() in self._loaded_properties

    def with_grid(self, grid: ReservoirGrid) -> "PropertyCollection":
        """Return a collection with all properties associated with a grid."""

        return PropertyCollection(
            properties=tuple(
                property_.with_grid(grid) for property_ in self.properties
            ),
            property_loaders={
                name: self._loader_with_grid(loader, grid)
                for name, loader in self.property_loaders.items()
            },
            source=self.source,
        )

    def _loader_with_grid(
        self,
        loader: Callable[[], GridProperty],
        grid: ReservoirGrid,
    ) -> Callable[[], GridProperty]:
        def load_with_grid() -> GridProperty:
            return loader().with_grid(grid)

        return load_with_grid
