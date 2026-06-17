"""GRDECL text writer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.keyword.keyword_record import KeywordRecord, KeywordValue


@dataclass(frozen=True, slots=True)
class GrdeclWriter:
    """Write GRDECL-style text keyword records.

    This writer targets the GRDECL-style text subset supported by the current
    readers. It does not write complete simulator decks or binary/formatted
    vendor variants.
    """

    values_per_line: int = 8

    def format_record(
        self,
        name: str,
        values: Iterable[KeywordValue],
    ) -> str:
        """Return one GRDECL keyword record."""

        keyword = name.strip().upper()
        if not keyword:
            raise ValueError("Keyword name must not be empty")
        materialized = tuple(values)
        if not materialized:
            return f"{keyword}\n/\n"

        lines = [keyword]
        for offset in range(0, len(materialized), self.values_per_line):
            chunk = materialized[offset : offset + self.values_per_line]
            lines.append("  " + " ".join(self._format_value(value) for value in chunk))
        lines.append("/")
        return "\n".join(lines) + "\n"

    def format_records(self, records: Iterable[KeywordRecord]) -> str:
        """Return multiple GRDECL records as text."""

        return "\n".join(
            self.format_record(record.name, record.values).rstrip()
            for record in records
        ) + "\n"

    def write_records(self, path: str | Path, records: Iterable[KeywordRecord]) -> None:
        """Write keyword records to a text file."""

        Path(path).write_text(self.format_records(records), encoding="utf-8")

    def _format_value(self, value: KeywordValue) -> str:
        if value is None:
            return "1*"
        if isinstance(value, bool):
            return "T" if value else "F"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return format(value, ".15g")
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
