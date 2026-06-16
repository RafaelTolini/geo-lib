"""GRDECL file reader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.exceptions.errors import FileReadError
from reservoir_data.formats.grdecl.parser import GrdeclParser


@dataclass(frozen=True, slots=True)
class GrdeclReader:
    """Read GRDECL text files into keyword datasets."""

    parser: GrdeclParser = field(default_factory=GrdeclParser)
    encoding: str = "utf-8"

    def read(self, path: str | Path) -> KeywordDataset:
        """Read and parse a GRDECL file."""

        source_path = Path(path)
        try:
            text = source_path.read_text(encoding=self.encoding)
        except OSError as error:
            raise FileReadError(f"Could not read GRDECL file {source_path}: {error}") from error
        return self.parser.parse_text(text, source=str(source_path))
