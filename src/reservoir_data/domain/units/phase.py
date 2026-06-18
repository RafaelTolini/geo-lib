"""Fluid phase value object."""

from __future__ import annotations

from enum import StrEnum


class Phase(StrEnum):
    """Known reservoir fluid phase labels."""

    OIL = "oil"
    WATER = "water"
    GAS = "gas"
    LIQUID = "liquid"
    VAPOR = "vapor"
    UNKNOWN = "unknown"

    @classmethod
    def from_label(cls, value: "Phase | str") -> "Phase":
        """Return a normalized phase from a user or file label."""

        if isinstance(value, cls):
            return value
        normalized = _normalize_label(value)
        try:
            return _PHASE_ALIASES[normalized]
        except KeyError as error:
            raise ValueError(f"Unknown phase label {value!r}") from error

    @classmethod
    def optional(cls, value: "Phase | str | None") -> "Phase | None":
        """Normalize an optional phase label."""

        if value is None:
            return None
        return cls.from_label(value)

    @property
    def is_known(self) -> bool:
        """Return whether this is a concrete phase."""

        return self is not Phase.UNKNOWN


def _normalize_label(value: str) -> str:
    label = value.strip()
    if not label:
        raise ValueError("phase label must not be empty")
    return label.replace("-", "_").replace(" ", "_").upper()


_PHASE_ALIASES: dict[str, Phase] = {
    "O": Phase.OIL,
    "OIL": Phase.OIL,
    "W": Phase.WATER,
    "WAT": Phase.WATER,
    "WATER": Phase.WATER,
    "G": Phase.GAS,
    "GAS": Phase.GAS,
    "LIQ": Phase.LIQUID,
    "LIQUID": Phase.LIQUID,
    "VAP": Phase.VAPOR,
    "VAPOR": Phase.VAPOR,
    "VAPOUR": Phase.VAPOR,
    "UNKNOWN": Phase.UNKNOWN,
}
