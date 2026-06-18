"""Formatted input-deck metadata reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from reservoir_data.domain.deck import DeckMetadata
from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.exceptions.errors import ParseError
from reservoir_data.formats.common.formatted_keyword_reader import (
    FormattedKeywordReader,
)


@dataclass(frozen=True, slots=True)
class FormattedDeckReader:
    """Read a narrow set of externally useful metadata from `.DATA` decks."""

    keyword_reader: FormattedKeywordReader = field(
        default_factory=FormattedKeywordReader
    )

    def read(self, path: str | Path) -> DeckMetadata:
        """Read deck metadata from a formatted keyword text deck."""

        source_path = Path(path)
        dataset = self.keyword_reader.read(source_path)
        title_record = dataset.record("TITLE", required=False)
        start_record = dataset.record("START", required=False)
        return DeckMetadata(
            title=None if title_record is None else _title_from_values(title_record.values),
            start_date=(
                None
                if start_record is None
                else _start_date_from_values(start_record.values)
            ),
            keyword_names=dataset.names(),
            source=str(source_path),
        )


def _title_from_values(values: tuple[KeywordValue, ...]) -> str | None:
    parts = tuple(str(value).strip() for value in values if value is not None)
    title = " ".join(part for part in parts if part)
    return title or None


def _start_date_from_values(values: tuple[KeywordValue, ...]) -> date:
    if len(values) == 1 and isinstance(values[0], str):
        text = values[0].strip()
        try:
            return date.fromisoformat(text)
        except ValueError:
            parts = tuple(part for part in text.replace(",", " ").split() if part)
            if len(parts) == 3:
                return _date_from_parts(parts)
            raise ParseError(f"Unsupported START date value {text!r}") from None

    if len(values) == 3:
        return _date_from_parts(values)

    raise ParseError(
        "START must contain either an ISO date string or day/month/year values"
    )


def _date_from_parts(values: tuple[KeywordValue, ...] | tuple[str, ...]) -> date:
    first, second, third = values
    if isinstance(first, int) and isinstance(second, int) and isinstance(third, int):
        if first > 31:
            return date(first, second, third)
        return date(third, second, first)
    if isinstance(first, int) and isinstance(second, str) and isinstance(third, int):
        return date(third, _month_number(second), first)
    if isinstance(first, str) and isinstance(second, str) and isinstance(third, str):
        day = int(first)
        return date(int(third), _month_number(second), day)
    raise ParseError(
        "START date values must be ISO, numeric year/month/day, or day/month/year"
    )


def _month_number(value: str) -> int:
    normalized = value.strip().upper()[:3]
    months = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }
    try:
        return months[normalized]
    except KeyError as error:
        raise ParseError(f"Unsupported START month {value!r}") from error
