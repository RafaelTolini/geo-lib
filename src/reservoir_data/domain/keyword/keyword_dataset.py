"""Ordered keyword dataset."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from reservoir_data.domain.keyword.keyword_record import KeywordRecord
from reservoir_data.domain.keyword.keyword_type import KeywordType
from reservoir_data.exceptions.errors import AmbiguousKeywordError, MissingKeywordError
from reservoir_data.schemas.queries import CaseSensitivity, KeywordQuery


@dataclass(frozen=True, slots=True)
class KeywordDataset:
    """Ordered collection of keyword records with occurrence-aware queries."""

    records: tuple[KeywordRecord, ...] = ()
    source: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))

    def __iter__(self) -> Iterator[KeywordRecord]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> KeywordRecord:
        return self.records[index]

    def names(self) -> tuple[str, ...]:
        """Return record names in original order."""

        return tuple(record.name for record in self.records)

    def has_keyword(
        self,
        name: str,
        case_sensitivity: CaseSensitivity = CaseSensitivity.INSENSITIVE,
    ) -> bool:
        """Return whether a keyword exists."""

        return bool(self.records_named(name, case_sensitivity))

    def records_named(
        self,
        name: str,
        case_sensitivity: CaseSensitivity = CaseSensitivity.INSENSITIVE,
    ) -> tuple[KeywordRecord, ...]:
        """Return all records matching a keyword name."""

        return tuple(
            record
            for record in self.records
            if self._names_match(record.name, name, case_sensitivity)
        )

    def record(
        self,
        name: str,
        occurrence_index: int = 0,
        expected_type: KeywordType | None = None,
        expected_size: int | None = None,
        case_sensitivity: CaseSensitivity = CaseSensitivity.INSENSITIVE,
        required: bool = True,
    ) -> KeywordRecord | None:
        """Return one keyword occurrence, validating optional expectations."""

        if occurrence_index < 0:
            raise ValueError("occurrence_index must be non-negative")

        matches = self.records_named(name, case_sensitivity)
        if occurrence_index >= len(matches):
            if required:
                raise MissingKeywordError(
                    f"Keyword {name!r} occurrence {occurrence_index} was not found"
                )
            return None

        return self._validate(matches[occurrence_index], expected_type, expected_size)

    def query(self, query: KeywordQuery) -> KeywordRecord | None:
        """Retrieve a record with a `KeywordQuery` contract."""

        matches = self.records_named(query.keyword_name, query.case_sensitivity)
        if query.occurrence_index is None:
            if not matches:
                if query.required:
                    raise MissingKeywordError(f"Keyword {query.keyword_name!r} was not found")
                return None
            if len(matches) > 1:
                raise AmbiguousKeywordError(
                    f"Keyword {query.keyword_name!r} has {len(matches)} occurrences; "
                    "specify occurrence_index"
                )
            return self._validate(matches[0], query.expected_type, query.expected_size)

        return self.record(
            name=query.keyword_name,
            occurrence_index=query.occurrence_index,
            expected_type=query.expected_type,
            expected_size=query.expected_size,
            case_sensitivity=query.case_sensitivity,
            required=query.required,
        )

    def filtered(
        self,
        name: str,
        case_sensitivity: CaseSensitivity = CaseSensitivity.INSENSITIVE,
    ) -> "KeywordDataset":
        """Return a dataset containing only matching keyword records."""

        return KeywordDataset(
            records=self.records_named(name, case_sensitivity),
            source=self.source,
        )

    def _validate(
        self,
        record: KeywordRecord,
        expected_type: KeywordType | None,
        expected_size: int | None,
    ) -> KeywordRecord:
        if expected_type is not None:
            record.require_type(expected_type)
        if expected_size is not None:
            record.require_size(expected_size)
        return record

    def _names_match(
        self, left: str, right: str, case_sensitivity: CaseSensitivity
    ) -> bool:
        normalized_policy = CaseSensitivity(case_sensitivity)
        if normalized_policy is CaseSensitivity.SENSITIVE:
            return left == right
        return left.casefold() == right.casefold()
