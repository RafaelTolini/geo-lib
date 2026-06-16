"""GRDECL text parser."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.keyword.keyword_record import KeywordRecord, KeywordValue
from reservoir_data.domain.keyword.keyword_type import KeywordType
from reservoir_data.exceptions.errors import ParseError
from reservoir_data.formats.grdecl.tokenizer import (
    GrdeclToken,
    GrdeclTokenizer,
    GrdeclTokenKind,
)


@dataclass(frozen=True, slots=True)
class _ParsedValue:
    value: KeywordValue
    keyword_type: KeywordType


@dataclass(frozen=True, slots=True)
class GrdeclParser:
    """Parse GRDECL text into neutral keyword records."""

    tokenizer: GrdeclTokenizer = GrdeclTokenizer()
    strict: bool = True

    _REPEAT_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<count>\d+)\*(?P<value>.*)$"
    )
    _INTEGER_RE: ClassVar[re.Pattern[str]] = re.compile(r"^[+-]?\d+$")
    _FLOAT_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^[+-]?(?:(?:\d+\.\d*)|(?:\.\d+)|(?:\d+))(?:[Ee][+-]?\d+)?$"
    )
    _DOUBLE_RE: ClassVar[re.Pattern[str]] = re.compile(
        r"^[+-]?(?:(?:\d+\.\d*)|(?:\.\d+)|(?:\d+))(?:[Dd][+-]?\d+)$"
    )
    _NUMERIC_PREFIX_RE: ClassVar[re.Pattern[str]] = re.compile(r"^[+-]?(?:\d|\.)")

    def parse_text(self, text: str, source: str | None = None) -> KeywordDataset:
        """Parse a GRDECL text string into a keyword dataset."""

        return self.parse_tokens(self.tokenizer.iter_tokens(text), source=source)

    def parse_tokens(
        self, tokens: Iterable[GrdeclToken], source: str | None = None
    ) -> KeywordDataset:
        """Parse pre-tokenized GRDECL input."""

        records: list[KeywordRecord] = []
        current_name: str | None = None
        value_tokens: list[GrdeclToken] = []

        for token in tokens:
            if token.kind is GrdeclTokenKind.TERMINATOR:
                if current_name is None:
                    raise ParseError(
                        f"Unexpected '/' at line {token.line}, column {token.column}"
                    )
                records.append(self._build_record(current_name, value_tokens, source))
                current_name = None
                value_tokens = []
                continue

            if current_name is None:
                current_name = self._parse_keyword_name(token)
            else:
                value_tokens.append(token)

        if current_name is not None:
            if self.strict:
                raise ParseError(f"Unterminated keyword record: {current_name}")
            records.append(self._build_record(current_name, value_tokens, source))

        return KeywordDataset(records=tuple(records), source=source)

    def _parse_keyword_name(self, token: GrdeclToken) -> str:
        if token.quoted:
            raise ParseError(
                f"Keyword name must not be quoted at line {token.line}, "
                f"column {token.column}"
            )
        name = token.text.strip().upper()
        if not name:
            raise ParseError(
                f"Empty keyword name at line {token.line}, column {token.column}"
            )
        return name

    def _build_record(
        self, name: str, tokens: list[GrdeclToken], source: str | None
    ) -> KeywordRecord:
        parsed_values: list[_ParsedValue] = []
        for token in tokens:
            parsed_values.extend(self._expand_token(token))
        values = tuple(parsed.value for parsed in parsed_values)
        keyword_type = self._infer_keyword_type(parsed_values)
        return KeywordRecord(
            name=name,
            values=values,
            keyword_type=keyword_type,
            source=source,
        )

    def _expand_token(self, token: GrdeclToken) -> tuple[_ParsedValue, ...]:
        repeat_match = self._REPEAT_RE.match(token.text)
        if repeat_match is None:
            return (self._parse_value(token.text, token.quoted),)

        count = int(repeat_match.group("count"))
        raw_value = repeat_match.group("value")
        if raw_value == "":
            repeated = _ParsedValue(None, KeywordType.DEFAULTED)
        else:
            repeated = self._parse_value(raw_value, token.quoted)
        return tuple(repeated for _ in range(count))

    def _parse_value(self, raw_value: str, quoted: bool) -> _ParsedValue:
        if quoted:
            return _ParsedValue(raw_value, KeywordType.STRING)

        normalized = raw_value.strip()
        logical_value = self._parse_logical(normalized)
        if logical_value is not None:
            return _ParsedValue(logical_value, KeywordType.LOGICAL)

        if self._INTEGER_RE.match(normalized):
            return _ParsedValue(int(normalized), KeywordType.INTEGER)

        if self._DOUBLE_RE.match(normalized):
            return _ParsedValue(
                float(normalized.replace("D", "E").replace("d", "e")),
                KeywordType.DOUBLE,
            )

        lower_normalized = normalized.lower()
        numeric_like = self._NUMERIC_PREFIX_RE.match(normalized) is not None
        if numeric_like and (
            "." in normalized or "e" in lower_normalized or "d" in lower_normalized
        ):
            if self._FLOAT_RE.match(normalized):
                return _ParsedValue(float(normalized), KeywordType.FLOAT)
            raise ParseError(f"Invalid numeric token: {raw_value!r}")

        return _ParsedValue(raw_value, KeywordType.STRING)

    def _parse_logical(self, normalized: str) -> bool | None:
        logical_token = normalized.strip(".").upper()
        if logical_token in {"T", "TRUE"}:
            return True
        if logical_token in {"F", "FALSE"}:
            return False
        return None

    def _infer_keyword_type(self, parsed_values: list[_ParsedValue]) -> KeywordType:
        observed = {parsed.keyword_type for parsed in parsed_values}
        if not observed:
            return KeywordType.DEFAULTED
        non_defaulted = observed - {KeywordType.DEFAULTED}
        if not non_defaulted:
            return KeywordType.DEFAULTED
        if non_defaulted == {KeywordType.INTEGER}:
            return KeywordType.INTEGER
        if non_defaulted <= {KeywordType.INTEGER, KeywordType.FLOAT}:
            return KeywordType.FLOAT
        if non_defaulted <= {
            KeywordType.INTEGER,
            KeywordType.FLOAT,
            KeywordType.DOUBLE,
        }:
            return KeywordType.DOUBLE
        if len(non_defaulted) == 1:
            return next(iter(non_defaulted))
        return KeywordType.MIXED
