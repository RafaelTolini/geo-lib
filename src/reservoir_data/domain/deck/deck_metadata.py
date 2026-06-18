"""Deck-level metadata domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DeckMetadata:
    """Externally useful metadata extracted from a simulator input deck."""

    title: str | None = None
    start_date: date | None = None
    keyword_names: tuple[str, ...] = ()
    source: str | None = None

    def __post_init__(self) -> None:
        if self.title is not None:
            title = self.title.strip()
            object.__setattr__(self, "title", title or None)
        object.__setattr__(
            self,
            "keyword_names",
            tuple(name.strip().upper() for name in self.keyword_names if name.strip()),
        )

    def has_keyword(self, name: str) -> bool:
        """Return whether the deck contains a keyword name."""

        normalized = name.strip().upper()
        if not normalized:
            raise ValueError("keyword name must not be empty")
        return normalized in self.keyword_names

    def keyword_count(self, name: str | None = None) -> int:
        """Return the total keyword count or occurrences of one keyword."""

        if name is None:
            return len(self.keyword_names)
        normalized = name.strip().upper()
        if not normalized:
            raise ValueError("keyword name must not be empty")
        return self.keyword_names.count(normalized)

    def unique_keyword_names(self) -> tuple[str, ...]:
        """Return keyword names in first-occurrence order."""

        return tuple(dict.fromkeys(self.keyword_names))
