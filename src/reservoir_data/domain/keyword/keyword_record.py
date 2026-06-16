"""Typed simulator keyword record."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from reservoir_data.domain.keyword.keyword_type import KeywordType
from reservoir_data.exceptions.errors import UnsupportedFormatError

KeywordValue = int | float | str | bool | None


@dataclass(frozen=True, slots=True)
class KeywordRecord:
    """One ordered keyword record with typed element values."""

    name: str
    values: tuple[KeywordValue, ...]
    keyword_type: KeywordType
    source: str | None = None

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().upper()
        if not normalized_name:
            raise ValueError("Keyword name must not be empty")
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "values", tuple(self.values))
        object.__setattr__(self, "keyword_type", KeywordType(self.keyword_type))
        for value in self.values:
            if not self._is_supported_value(value):
                raise UnsupportedFormatError(
                    f"Unsupported value type for keyword {self.name}: "
                    f"{type(value).__name__}"
                )

    @classmethod
    def from_values(
        cls,
        name: str,
        values: Iterable[KeywordValue],
        keyword_type: KeywordType | None = None,
        source: str | None = None,
    ) -> "KeywordRecord":
        """Build a record and infer the element type when not supplied."""

        materialized = tuple(values)
        inferred_type = keyword_type or infer_keyword_type(materialized)
        return cls(
            name=name,
            values=materialized,
            keyword_type=inferred_type,
            source=source,
        )

    @property
    def element_count(self) -> int:
        """Number of values in the record."""

        return len(self.values)

    def scalar(self) -> KeywordValue:
        """Return the only value in a scalar record."""

        if len(self.values) != 1:
            raise ValueError(
                f"Keyword {self.name} contains {len(self.values)} values, not one"
            )
        return self.values[0]

    def copy_values(self) -> tuple[KeywordValue, ...]:
        """Return an immutable copy-friendly value tuple."""

        return tuple(self.values)

    def require_type(self, expected_type: KeywordType) -> "KeywordRecord":
        """Validate the record type and return this record for fluent use."""

        normalized_type = KeywordType(expected_type)
        if self.keyword_type != normalized_type:
            raise UnsupportedFormatError(
                f"Keyword {self.name} has type {self.keyword_type}; "
                f"expected {normalized_type}"
            )
        return self

    def require_size(self, expected_size: int) -> "KeywordRecord":
        """Validate the record element count and return this record."""

        if expected_size < 0:
            raise ValueError("expected_size must be non-negative")
        if self.element_count != expected_size:
            raise ValueError(
                f"Keyword {self.name} has {self.element_count} values; "
                f"expected {expected_size}"
            )
        return self

    def _is_supported_value(self, value: object) -> bool:
        return value is None or isinstance(value, (bool, int, float, str))


def infer_keyword_type(values: Iterable[KeywordValue]) -> KeywordType:
    """Infer a conservative keyword type from Python values."""

    observed: set[KeywordType] = set()
    for value in values:
        if value is None:
            observed.add(KeywordType.DEFAULTED)
        elif isinstance(value, bool):
            observed.add(KeywordType.LOGICAL)
        elif isinstance(value, int):
            observed.add(KeywordType.INTEGER)
        elif isinstance(value, float):
            observed.add(KeywordType.FLOAT)
        elif isinstance(value, str):
            observed.add(KeywordType.STRING)
        else:
            raise UnsupportedFormatError(
                f"Unsupported keyword value type: {type(value).__name__}"
            )

    if not observed:
        return KeywordType.DEFAULTED
    non_defaulted = observed - {KeywordType.DEFAULTED}
    if not non_defaulted:
        return KeywordType.DEFAULTED
    if non_defaulted == {KeywordType.INTEGER}:
        return KeywordType.INTEGER
    if non_defaulted <= {KeywordType.INTEGER, KeywordType.FLOAT}:
        return (
            KeywordType.FLOAT
            if KeywordType.FLOAT in non_defaulted
            else KeywordType.INTEGER
        )
    if len(non_defaulted) == 1:
        return next(iter(non_defaulted))
    return KeywordType.MIXED
