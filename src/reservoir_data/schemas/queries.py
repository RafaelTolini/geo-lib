"""Query schemas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from reservoir_data.domain.keyword.keyword_type import KeywordType


class CaseSensitivity(StrEnum):
    """Case matching policy for keyword queries."""

    INSENSITIVE = "insensitive"
    SENSITIVE = "sensitive"


@dataclass(frozen=True, slots=True)
class KeywordQuery:
    """Typed contract for retrieving a keyword record."""

    keyword_name: str
    occurrence_index: int | None = 0
    expected_type: KeywordType | None = None
    expected_size: int | None = None
    case_sensitivity: CaseSensitivity = CaseSensitivity.INSENSITIVE
    required: bool = True

    def __post_init__(self) -> None:
        normalized_name = self.keyword_name.strip()
        if not normalized_name:
            raise ValueError("keyword_name must not be empty")
        object.__setattr__(self, "keyword_name", normalized_name)

        if self.occurrence_index is not None and self.occurrence_index < 0:
            raise ValueError("occurrence_index must be non-negative")
        if self.expected_type is not None:
            object.__setattr__(self, "expected_type", KeywordType(self.expected_type))
        if self.expected_size is not None and self.expected_size < 0:
            raise ValueError("expected_size must be non-negative")
        object.__setattr__(
            self, "case_sensitivity", CaseSensitivity(self.case_sensitivity)
        )
