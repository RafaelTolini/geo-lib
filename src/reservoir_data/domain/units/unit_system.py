"""Unit-system value object."""

from __future__ import annotations

from enum import StrEnum


class UnitSystem(StrEnum):
    """Known simulator unit-system labels.

    This enum intentionally identifies unit-system metadata only. Numeric unit
    conversion is a separate behavior and is not inferred from the label here.
    """

    METRIC = "metric"
    FIELD = "field"
    LAB = "lab"
    SI = "si"
    UNKNOWN = "unknown"

    @classmethod
    def from_label(cls, value: "UnitSystem | str") -> "UnitSystem":
        """Return a normalized unit-system value from a user or file label."""

        if isinstance(value, cls):
            return value
        normalized = _normalize_label(value)
        try:
            return _UNIT_SYSTEM_ALIASES[normalized]
        except KeyError as error:
            raise ValueError(f"Unknown unit system label {value!r}") from error

    @classmethod
    def optional(cls, value: "UnitSystem | str | None") -> "UnitSystem | None":
        """Normalize an optional unit-system label."""

        if value is None:
            return None
        return cls.from_label(value)

    @property
    def is_known(self) -> bool:
        """Return whether this is a concrete unit system."""

        return self is not UnitSystem.UNKNOWN


def _normalize_label(value: str) -> str:
    label = value.strip()
    if not label:
        raise ValueError("unit system label must not be empty")
    return label.replace("-", "_").replace(" ", "_").upper()


_UNIT_SYSTEM_ALIASES: dict[str, UnitSystem] = {
    "METRIC": UnitSystem.METRIC,
    "METRICS": UnitSystem.METRIC,
    "MET": UnitSystem.METRIC,
    "FIELD": UnitSystem.FIELD,
    "FIELD_UNITS": UnitSystem.FIELD,
    "FIELDUNITS": UnitSystem.FIELD,
    "FLD": UnitSystem.FIELD,
    "LAB": UnitSystem.LAB,
    "LABORATORY": UnitSystem.LAB,
    "SI": UnitSystem.SI,
    "S_I": UnitSystem.SI,
    "UNKNOWN": UnitSystem.UNKNOWN,
}
