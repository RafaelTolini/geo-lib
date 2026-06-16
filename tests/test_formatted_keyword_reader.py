from pathlib import Path
import struct

import pytest

from reservoir_data.exceptions.errors import FileReadError, ParseError
from reservoir_data.formats.common.formatted_keyword_reader import FormattedKeywordReader
from reservoir_data.infrastructure.binary_io.endianness import Endianness


def _record(payload: bytes, endianness: Endianness = Endianness.LITTLE) -> bytes:
    marker = struct.pack(f"{endianness.struct_prefix}I", len(payload))
    return marker + payload + marker


def test_formatted_keyword_reader_parses_text_keywords() -> None:
    dataset = FormattedKeywordReader().parse_text("PORO 2*0.25 / PERMX 10 20 /")

    assert dataset.record("PORO").values == (0.25, 0.25)
    assert dataset.record("PERMX").values == (10, 20)


def test_formatted_keyword_reader_reads_file(tmp_path: Path) -> None:
    path = tmp_path / "props.fkw"
    path.write_text("ACTNUM 1 0 1 /", encoding="utf-8")

    dataset = FormattedKeywordReader().read(path)

    assert dataset.source == str(path)
    assert dataset.record("ACTNUM").values == (1, 0, 1)


def test_formatted_keyword_reader_reports_missing_and_binary_inputs(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileReadError):
        FormattedKeywordReader().read(tmp_path / "missing.fkw")

    with pytest.raises(ParseError, match="binary-looking"):
        FormattedKeywordReader().parse_bytes(_record(b"PORO 1 /", Endianness.LITTLE))

    with pytest.raises(ParseError, match="decode"):
        FormattedKeywordReader().parse_bytes(b"\xff\xfe\xfd")
