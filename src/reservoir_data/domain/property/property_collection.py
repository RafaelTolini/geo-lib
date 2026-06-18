"""Collection of grid properties."""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path

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
        return normalized_name in self.names()

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

    def select(self, names: tuple[str, ...] | list[str]) -> "PropertyCollection":
        """Return a collection exposing only selected property names."""

        selected_names = tuple(name.strip().upper() for name in names if name.strip())
        loaded: list[GridProperty] = []
        loaders: dict[str, Callable[[], GridProperty]] = {}
        for name in selected_names:
            if name in self._loaded_properties:
                loaded.append(self._loaded_properties[name])
            elif name in self.property_loaders:
                loaders[name] = self.property_loaders[name]
            else:
                raise MissingKeywordError(f"Property {name!r} was not found")
        return PropertyCollection(
            properties=tuple(loaded),
            property_loaders=loaders,
            source=self.source,
        )

    def materialize(self, names: Iterable[str] | None = None) -> "PropertyCollection":
        """Return a collection with selected lazy properties loaded eagerly."""

        selected_names = self.names() if names is None else tuple(names)
        return PropertyCollection(
            properties=tuple(self.property(name) for name in selected_names),
            source=self.source,
        )

    def metadata_rows(self) -> tuple[dict[str, object], ...]:
        """Return property metadata rows without forcing lazy loads."""

        rows: list[dict[str, object]] = []
        for index, name in enumerate(self.names()):
            property_ = self._loaded_properties.get(name)
            rows.append(
                {
                    "INDEX": index,
                    "PROPERTY": name,
                    "LOADED": property_ is not None,
                    "LAYOUT": None if property_ is None else property_.layout.value,
                    "VALUE_COUNT": None if property_ is None else property_.value_count,
                    "UNIT": None if property_ is None else property_.unit,
                    "SOURCE": self.source,
                }
            )
        return tuple(rows)

    def metadata_to_csv(self, path: str | Path) -> None:
        """Write property metadata rows to CSV."""

        fieldnames = [
            "INDEX",
            "PROPERTY",
            "LOADED",
            "LAYOUT",
            "VALUE_COUNT",
            "UNIT",
            "SOURCE",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.metadata_rows())

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
