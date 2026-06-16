"""Active/global cell mapping."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from reservoir_data.exceptions.errors import InvalidCellIndexError, PropertyShapeError

CellValue = int | float | bool | str | None


@dataclass(frozen=True, slots=True)
class ActiveCellMap:
    """Relationship between global cells and active cells."""

    activity_mask: tuple[bool, ...]

    def __post_init__(self) -> None:
        mask = tuple(bool(value) for value in self.activity_mask)
        object.__setattr__(self, "activity_mask", mask)

    @classmethod
    def all_active(cls, total_cell_count: int) -> "ActiveCellMap":
        """Create a map where every global cell is active."""

        if total_cell_count < 0:
            raise ValueError("total_cell_count must be non-negative")
        return cls(activity_mask=tuple(True for _ in range(total_cell_count)))

    @classmethod
    def from_activity_values(
        cls, values: Sequence[int | bool], total_cell_count: int
    ) -> "ActiveCellMap":
        """Create a map from ACTNUM-like values."""

        if len(values) != total_cell_count:
            raise PropertyShapeError(
                f"Activity mask has {len(values)} values; expected {total_cell_count}"
            )
        return cls(activity_mask=tuple(bool(value) for value in values))

    @property
    def total_cell_count(self) -> int:
        """Number of global cells represented by the map."""

        return len(self.activity_mask)

    @property
    def active_cell_count(self) -> int:
        """Number of active cells."""

        return sum(1 for is_active in self.activity_mask if is_active)

    @property
    def active_to_global(self) -> tuple[int, ...]:
        """Mapping from zero-based active index to zero-based global index."""

        return tuple(
            global_index
            for global_index, is_active in enumerate(self.activity_mask)
            if is_active
        )

    @property
    def global_to_active(self) -> tuple[int | None, ...]:
        """Mapping from zero-based global index to active index, or `None`."""

        active_lookup: list[int | None] = []
        next_active = 0
        for is_active in self.activity_mask:
            if is_active:
                active_lookup.append(next_active)
                next_active += 1
            else:
                active_lookup.append(None)
        return tuple(active_lookup)

    def is_active_global(self, global_index: int) -> bool:
        """Return whether a zero-based global cell is active."""

        self._require_global_index(global_index)
        return self.activity_mask[global_index]

    def global_to_active_index(self, global_index: int) -> int | None:
        """Return active index for a global cell, or `None` for inactive cells."""

        self._require_global_index(global_index)
        return self.global_to_active[global_index]

    def active_to_global_index(self, active_index: int) -> int:
        """Return global index for a zero-based active index."""

        self._require_active_index(active_index)
        return self.active_to_global[active_index]

    def to_global(
        self,
        active_values: Sequence[CellValue] | object,
        default_value: CellValue = None,
    ) -> tuple[CellValue, ...] | object:
        """Expand active-sized values to global-sized values."""

        if self._is_numpy_array(active_values):
            return self._numpy_to_global(active_values, default_value)

        if not isinstance(active_values, Sequence):
            raise PropertyShapeError("Active values must be a sequence")
        if len(active_values) != self.active_cell_count:
            raise PropertyShapeError(
                f"Active values have {len(active_values)} elements; expected "
                f"{self.active_cell_count}"
            )

        global_values: list[CellValue] = [
            default_value for _ in range(self.total_cell_count)
        ]
        for active_index, global_index in enumerate(self.active_to_global):
            global_values[global_index] = active_values[active_index]
        return tuple(global_values)

    def compress_global(
        self, global_values: Sequence[CellValue] | object
    ) -> tuple[CellValue, ...] | object:
        """Compress global-sized values to active-sized values."""

        if self._is_numpy_array(global_values):
            return self._numpy_compress_global(global_values)

        if not isinstance(global_values, Sequence):
            raise PropertyShapeError("Global values must be a sequence")
        if len(global_values) != self.total_cell_count:
            raise PropertyShapeError(
                f"Global values have {len(global_values)} elements; expected "
                f"{self.total_cell_count}"
            )
        return tuple(global_values[global_index] for global_index in self.active_to_global)

    def _require_global_index(self, global_index: int) -> None:
        if not 0 <= global_index < self.total_cell_count:
            raise InvalidCellIndexError(
                f"Global cell index {global_index} is outside active map bounds"
            )

    def _require_active_index(self, active_index: int) -> None:
        if not 0 <= active_index < self.active_cell_count:
            raise InvalidCellIndexError(
                f"Active cell index {active_index} is outside active map bounds"
            )

    def _is_numpy_array(self, value: object) -> bool:
        numpy = self._numpy_module()
        return numpy is not None and isinstance(value, numpy.ndarray)

    def _numpy_to_global(self, active_values: object, default_value: CellValue) -> object:
        numpy = self._numpy_module()
        if numpy is None:
            raise PropertyShapeError("NumPy is not available")
        if active_values.ndim != 1 or active_values.shape[0] != self.active_cell_count:
            raise PropertyShapeError(
                f"Active NumPy array has shape {active_values.shape}; expected "
                f"({self.active_cell_count},)"
            )
        dtype = active_values.dtype if default_value is not None else object
        global_values = numpy.empty(self.total_cell_count, dtype=dtype)
        global_values.fill(default_value)
        global_values[list(self.active_to_global)] = active_values
        return global_values

    def _numpy_compress_global(self, global_values: object) -> object:
        if global_values.ndim != 1 or global_values.shape[0] != self.total_cell_count:
            raise PropertyShapeError(
                f"Global NumPy array has shape {global_values.shape}; expected "
                f"({self.total_cell_count},)"
            )
        return global_values[list(self.active_to_global)]

    def _numpy_module(self) -> object | None:
        try:
            import numpy
        except ModuleNotFoundError:
            return None
        return numpy
