"""Grid-associated property array."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from reservoir_data.domain.grid.cell_index import CellIndex
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_record import (
    KeywordRecord,
    KeywordValue,
    NumericKeywordValue,
)
from reservoir_data.exceptions.errors import (
    InvalidCellIndexError,
    PropertyShapeError,
    UnsupportedFormatError,
)


class PropertyLayout(StrEnum):
    """How a property value array relates to the grid."""

    ACTIVE = "active"
    GLOBAL = "global"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class GridProperty:
    """A named property associated with a structured grid when available."""

    name: str
    values: tuple[KeywordValue, ...]
    layout: PropertyLayout = PropertyLayout.UNKNOWN
    grid: ReservoirGrid | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().upper()
        if not normalized_name:
            raise ValueError("Property name must not be empty")
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "values", tuple(self.values))
        object.__setattr__(self, "layout", PropertyLayout(self.layout))
        if self.grid is not None:
            self._validate_shape(self.grid)

    @classmethod
    def from_record(
        cls,
        record: KeywordRecord,
        grid: ReservoirGrid | None = None,
        unit: str | None = None,
    ) -> "GridProperty":
        """Create a property from a keyword record."""

        layout = cls._infer_layout(len(record.values), grid)
        return cls(
            name=record.name,
            values=record.values,
            layout=layout,
            grid=grid,
            unit=unit,
        )

    @property
    def value_count(self) -> int:
        """Number of stored values."""

        return len(self.values)

    def with_grid(self, grid: ReservoirGrid) -> "GridProperty":
        """Return a copy associated with a grid and inferred layout."""

        return GridProperty(
            name=self.name,
            values=self.values,
            layout=self._infer_layout(len(self.values), grid),
            grid=grid,
            unit=self.unit,
        )

    def to_global_array(
        self, default_value: KeywordValue = None
    ) -> tuple[KeywordValue, ...]:
        """Return global-sized values."""

        grid = self._require_grid()
        if self.layout is PropertyLayout.GLOBAL:
            return tuple(self.values)
        if self.layout is PropertyLayout.ACTIVE:
            converted = grid.active_cell_map.to_global(self.values, default_value)
            if not isinstance(converted, tuple):
                raise PropertyShapeError("Expected tuple conversion for sequence input")
            return converted
        raise PropertyShapeError(
            f"Property {self.name} layout is unknown and cannot be expanded"
        )

    def to_active_array(self) -> tuple[KeywordValue, ...]:
        """Return active-sized values."""

        grid = self._require_grid()
        if self.layout is PropertyLayout.ACTIVE:
            return tuple(self.values)
        if self.layout is PropertyLayout.GLOBAL:
            converted = grid.active_cell_map.compress_global(self.values)
            if not isinstance(converted, tuple):
                raise PropertyShapeError("Expected tuple conversion for sequence input")
            return converted
        raise PropertyShapeError(
            f"Property {self.name} layout is unknown and cannot be compressed"
        )

    def value_at(self, index: CellIndex) -> KeywordValue:
        """Evaluate this property at a grid cell."""

        grid = self._require_grid()
        if self.layout is PropertyLayout.GLOBAL:
            return self.values[grid.global_index(index)]
        if self.layout is PropertyLayout.ACTIVE:
            active_index = grid.active_index(index)
            if active_index is None:
                raise InvalidCellIndexError(
                    f"Property {self.name} has no active value for inactive cell"
                )
            return self.values[active_index]
        raise PropertyShapeError(
            f"Property {self.name} layout is unknown and cannot be evaluated"
        )

    def numeric_values(
        self,
        layout: PropertyLayout | str | None = None,
        default_value: NumericKeywordValue | None = None,
    ) -> tuple[NumericKeywordValue, ...]:
        """Return numeric values in the requested layout."""

        values = self._values_for_layout(layout, default_value=default_value)
        return KeywordRecord.from_values(self.name, values).numeric_values(
            default_value=default_value
        )

    def to_numpy(
        self,
        layout: PropertyLayout | str | None = None,
        default_value: NumericKeywordValue | None = None,
        dtype: object | None = None,
    ) -> object:
        """Return property values as a NumPy array when NumPy is installed."""

        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError as error:
            raise UnsupportedFormatError("NumPy is not installed") from error
        return np.asarray(
            self.numeric_values(layout=layout, default_value=default_value),
            dtype=dtype,
        )

    def _require_grid(self) -> ReservoirGrid:
        if self.grid is None:
            raise PropertyShapeError(
                f"Property {self.name} is not associated with a grid"
            )
        return self.grid

    def _values_for_layout(
        self,
        layout: PropertyLayout | str | None,
        default_value: KeywordValue,
    ) -> tuple[KeywordValue, ...]:
        if layout is None:
            return tuple(self.values)

        target_layout = PropertyLayout(layout)
        if target_layout is PropertyLayout.ACTIVE:
            return self.to_active_array()
        if target_layout is PropertyLayout.GLOBAL:
            return self.to_global_array(default_value=default_value)
        if self.layout is PropertyLayout.UNKNOWN:
            return tuple(self.values)
        raise PropertyShapeError(
            f"Property {self.name} has known layout {self.layout}; "
            "use ACTIVE or GLOBAL when requesting converted values"
        )

    def _validate_shape(self, grid: ReservoirGrid) -> None:
        if self.layout is PropertyLayout.GLOBAL and len(self.values) != grid.total_cell_count:
            raise PropertyShapeError(
                f"Property {self.name} has {len(self.values)} values; expected "
                f"{grid.total_cell_count} global values"
            )
        if self.layout is PropertyLayout.ACTIVE and len(self.values) != grid.active_cell_count:
            raise PropertyShapeError(
                f"Property {self.name} has {len(self.values)} values; expected "
                f"{grid.active_cell_count} active values"
            )
        if self.layout is PropertyLayout.UNKNOWN:
            raise PropertyShapeError(
                f"Property {self.name} has {len(self.values)} values, which does "
                "not match active or global grid shape"
            )

    @staticmethod
    def _infer_layout(
        value_count: int, grid: ReservoirGrid | None
    ) -> PropertyLayout:
        if grid is None:
            return PropertyLayout.UNKNOWN
        if value_count == grid.total_cell_count:
            return PropertyLayout.GLOBAL
        if value_count == grid.active_cell_count:
            return PropertyLayout.ACTIVE
        return PropertyLayout.UNKNOWN
