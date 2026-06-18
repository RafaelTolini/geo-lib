"""Common formatted text keyword reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.exceptions.errors import FileReadError, ParseError, UnsupportedFormatError
from reservoir_data.formats.grdecl.parser import GrdeclParser


@dataclass(frozen=True, slots=True)
class FormattedKeywordReader:
    """Read GRDECL-style formatted text keyword records.

    This reader is common infrastructure for later format-specific readers. It
    does not claim support for every simulator formatted variant; it reads the
    text keyword syntax already implemented by `GrdeclParser`.
    """

    parser: GrdeclParser = field(default_factory=GrdeclParser)
    encoding: str = "utf-8"

    def read(
        self,
        path: str | Path,
        expect_formatted: bool | None = True,
    ) -> KeywordDataset:
        """Read a formatted keyword text file."""

        source_path = Path(path)
        try:
            data = source_path.read_bytes()
        except OSError as error:
            raise FileReadError(
                f"Could not read formatted keyword file {source_path}: {error}"
            ) from error
        return self.parse_bytes(
            data,
            source=str(source_path),
            expect_formatted=expect_formatted,
        )

    def parse_bytes(
        self,
        data: bytes,
        source: str | None = None,
        expect_formatted: bool | None = True,
    ) -> KeywordDataset:
        """Decode bytes and parse formatted keyword records."""

        if expect_formatted is False:
            raise UnsupportedFormatError(
                "FormattedKeywordReader cannot read explicitly unformatted payloads"
            )
        if b"\x00" in data:
            raise ParseError(
                "Formatted keyword reader received binary-looking data; "
                "use an unformatted record reader instead"
            )
        try:
            text = data.decode(self.encoding)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Could not decode formatted keyword data as {self.encoding}"
            ) from error
        return self.parse_text(text, source=source)

    def parse_text(self, text: str, source: str | None = None) -> KeywordDataset:
        """Parse formatted keyword records from text."""

        if "\x00" in text:
            raise ParseError(
                "Formatted keyword reader received binary-looking text; "
                "use an unformatted record reader instead"
            )
        return self.parser.parse_text(text, source=source)
