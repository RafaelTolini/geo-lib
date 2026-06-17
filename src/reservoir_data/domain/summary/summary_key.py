"""Summary vector key value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SummaryKey:
    """Canonical key for one summary vector."""

    keyword: str
    qualifier: str | None = None
    qualifier_kind: str | None = None

    def __post_init__(self) -> None:
        keyword = self.keyword.strip().upper()
        if not keyword:
            raise ValueError("Summary keyword must not be empty")
        if ":" in keyword:
            raise ValueError("Summary keyword must not contain ':'")
        object.__setattr__(self, "keyword", keyword)

        if self.qualifier is not None:
            qualifier = self.qualifier.strip()
            if not qualifier:
                qualifier = None
            if qualifier is not None and ":" in qualifier:
                raise ValueError("Summary qualifier must not contain ':'")
            object.__setattr__(self, "qualifier", qualifier)

        if self.qualifier_kind is not None:
            qualifier_kind = self.qualifier_kind.strip().lower()
            if not qualifier_kind:
                qualifier_kind = None
            object.__setattr__(self, "qualifier_kind", qualifier_kind)

    @property
    def canonical(self) -> str:
        """Return the stable public key string."""

        if self.qualifier is None:
            return self.keyword
        return f"{self.keyword}:{self.qualifier}"

    @classmethod
    def parse(cls, value: str) -> "SummaryKey":
        """Parse a public key string."""

        parts = value.strip().split(":", maxsplit=1)
        if len(parts) == 1:
            return cls(keyword=parts[0])
        return cls(keyword=parts[0], qualifier=parts[1])
