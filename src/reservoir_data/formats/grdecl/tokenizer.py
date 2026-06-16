"""GRDECL text tokenizer."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from reservoir_data.exceptions.errors import ParseError


class GrdeclTokenKind(StrEnum):
    """Kinds emitted by the GRDECL tokenizer."""

    VALUE = "value"
    TERMINATOR = "terminator"


@dataclass(frozen=True, slots=True)
class GrdeclToken:
    """One token with source position metadata."""

    text: str
    line: int
    column: int
    kind: GrdeclTokenKind = GrdeclTokenKind.VALUE
    quoted: bool = False


@dataclass(frozen=True, slots=True)
class GrdeclTokenizer:
    """Tokenize GRDECL text without interpreting keyword values."""

    def tokenize(self, text: str) -> tuple[GrdeclToken, ...]:
        """Return all tokens from a text block."""

        return tuple(self.iter_tokens(text))

    def iter_tokens(self, text: str) -> Iterator[GrdeclToken]:
        """Yield tokens from a text block."""

        buffer: list[str] = []
        token_line = 1
        token_column = 1
        token_quoted = False
        token_active = False
        line = 1
        column = 1
        index = 0

        def start_token_if_needed() -> None:
            nonlocal token_active, token_line, token_column
            if not token_active:
                token_line = line
                token_column = column
                token_active = True

        def flush_token() -> GrdeclToken | None:
            nonlocal token_active, token_quoted
            if not token_active:
                return None
            token = GrdeclToken(
                text="".join(buffer),
                line=token_line,
                column=token_column,
                kind=GrdeclTokenKind.VALUE,
                quoted=token_quoted,
            )
            buffer.clear()
            token_active = False
            token_quoted = False
            return token

        while index < len(text):
            character = text[index]
            next_character = text[index + 1] if index + 1 < len(text) else ""

            if character == "\r":
                token = flush_token()
                if token is not None:
                    yield token
                if next_character == "\n":
                    index += 1
                line += 1
                column = 1
                index += 1
                continue

            if character == "\n":
                token = flush_token()
                if token is not None:
                    yield token
                line += 1
                column = 1
                index += 1
                continue

            if character.isspace():
                token = flush_token()
                if token is not None:
                    yield token
                column += 1
                index += 1
                continue

            if character == "-" and next_character == "-":
                token = flush_token()
                if token is not None:
                    yield token
                index += 2
                column += 2
                while index < len(text) and text[index] not in "\r\n":
                    index += 1
                    column += 1
                continue

            if character == "#":
                token = flush_token()
                if token is not None:
                    yield token
                index += 1
                column += 1
                while index < len(text) and text[index] not in "\r\n":
                    index += 1
                    column += 1
                continue

            if character == "/":
                token = flush_token()
                if token is not None:
                    yield token
                yield GrdeclToken(
                    text="/",
                    line=line,
                    column=column,
                    kind=GrdeclTokenKind.TERMINATOR,
                )
                index += 1
                column += 1
                continue

            if character in {"'", '"'}:
                start_token_if_needed()
                token_quoted = True
                quote_character = character
                index += 1
                column += 1
                while index < len(text):
                    quoted_character = text[index]
                    following_character = (
                        text[index + 1] if index + 1 < len(text) else ""
                    )
                    if quoted_character == quote_character:
                        if following_character == quote_character:
                            buffer.append(quote_character)
                            index += 2
                            column += 2
                            continue
                        index += 1
                        column += 1
                        break
                    buffer.append(quoted_character)
                    if quoted_character == "\r":
                        if following_character == "\n":
                            index += 1
                        line += 1
                        column = 1
                    elif quoted_character == "\n":
                        line += 1
                        column = 1
                    else:
                        column += 1
                    index += 1
                else:
                    raise ParseError(
                        f"Unterminated quoted string starting at "
                        f"line {token_line}, column {token_column}"
                    )
                continue

            start_token_if_needed()
            buffer.append(character)
            index += 1
            column += 1

        token = flush_token()
        if token is not None:
            yield token
