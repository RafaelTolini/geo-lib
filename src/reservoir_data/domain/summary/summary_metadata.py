"""Summary metadata domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase

from reservoir_data.domain.summary.summary_key import SummaryKey
from reservoir_data.exceptions.errors import MissingKeywordError, SummaryDataError


@dataclass(frozen=True, slots=True)
class SummaryVectorMetadata:
    """Metadata for one summary vector."""

    key: SummaryKey
    unit: str | None = None
    classification: str | None = None

    def __post_init__(self) -> None:
        if self.unit is not None:
            unit = self.unit.strip()
            object.__setattr__(self, "unit", unit or None)
        if self.classification is not None:
            classification = self.classification.strip().lower()
            object.__setattr__(self, "classification", classification or None)


@dataclass(frozen=True, slots=True)
class SummaryMetadata:
    """Summary vector catalog."""

    vectors: tuple[SummaryVectorMetadata, ...]
    source: str | None = None

    def __post_init__(self) -> None:
        vectors = tuple(self.vectors)
        if not vectors:
            raise SummaryDataError("Summary metadata contains no vectors")
        canonical_keys = [item.key.canonical for item in vectors]
        duplicates = {
            key for key in canonical_keys if canonical_keys.count(key) > 1
        }
        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise SummaryDataError(f"Duplicate summary vector metadata: {duplicate_list}")
        object.__setattr__(self, "vectors", vectors)

    def keys(self) -> tuple[str, ...]:
        """Return canonical vector keys in metadata order."""

        return tuple(item.key.canonical for item in self.vectors)

    def vector_metadata(self, key: str | SummaryKey) -> SummaryVectorMetadata:
        """Return metadata for one vector."""

        canonical = self._canonical(key)
        for item in self.vectors:
            if item.key.canonical == canonical:
                return item
        raise MissingKeywordError(f"Summary vector {canonical!r} was not found")

    def filter_keys(
        self,
        pattern: str = "*",
        keyword: str | None = None,
        qualifier: str | None = None,
        qualifier_kind: str | None = None,
    ) -> tuple[str, ...]:
        """Filter vector keys by wildcard and optional semantic qualifiers."""

        normalized_keyword = None if keyword is None else keyword.strip().upper()
        normalized_qualifier = None if qualifier is None else qualifier.strip()
        normalized_kind = None if qualifier_kind is None else qualifier_kind.strip().lower()
        normalized_pattern = pattern.strip().upper() or "*"

        matches: list[str] = []
        for item in self.vectors:
            key = item.key
            if not fnmatchcase(key.canonical.upper(), normalized_pattern):
                continue
            if normalized_keyword is not None and key.keyword != normalized_keyword:
                continue
            if normalized_qualifier is not None and key.qualifier != normalized_qualifier:
                continue
            if normalized_kind is not None and key.qualifier_kind != normalized_kind:
                continue
            matches.append(key.canonical)
        return tuple(matches)

    def _canonical(self, key: str | SummaryKey) -> str:
        if isinstance(key, SummaryKey):
            return key.canonical
        return SummaryKey.parse(key).canonical
