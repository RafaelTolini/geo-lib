from pathlib import Path

import pytest

from reservoir_data.domain.keyword.keyword_type import KeywordType
from reservoir_data.exceptions.errors import FileReadError, ParseError
from reservoir_data.formats.grdecl.parser import GrdeclParser
from reservoir_data.formats.grdecl.reader import GrdeclReader
from reservoir_data.formats.grdecl.tokenizer import GrdeclTokenizer, GrdeclTokenKind


def test_grdecl_parser_handles_core_value_types_comments_and_repeats() -> None:
    text = """
    -- leading comment
    SPECGRID
      2 2 1 1 F / # trailing comment
    PORO
      2*0.25 1.0E-1 1.0D+0 /
    NAMES
      'PROD-1' 2*'INJ A' FIELD /
    FLAGS
      T .FALSE. TRUE F /
    DEFAULTS
      3* /
    EMPTYSTR
      '' /
    """

    dataset = GrdeclParser().parse_text(text, source="inline")

    assert dataset.names() == (
        "SPECGRID",
        "PORO",
        "NAMES",
        "FLAGS",
        "DEFAULTS",
        "EMPTYSTR",
    )
    assert dataset.record("SPECGRID").values == (2, 2, 1, 1, False)
    assert dataset.record("SPECGRID").keyword_type == KeywordType.MIXED
    assert dataset.record("PORO").values == (0.25, 0.25, 0.1, 1.0)
    assert dataset.record("PORO").keyword_type == KeywordType.DOUBLE
    assert dataset.record("NAMES").values == ("PROD-1", "INJ A", "INJ A", "FIELD")
    assert dataset.record("NAMES").keyword_type == KeywordType.STRING
    assert dataset.record("FLAGS").values == (True, False, True, False)
    assert dataset.record("FLAGS").keyword_type == KeywordType.LOGICAL
    assert dataset.record("DEFAULTS").values == (None, None, None)
    assert dataset.record("DEFAULTS").keyword_type == KeywordType.DEFAULTED
    assert dataset.record("EMPTYSTR").values == ("",)


def test_grdecl_tokenizer_preserves_quoted_slashes_and_escaped_quotes() -> None:
    tokens = GrdeclTokenizer().tokenize("TITLE 'A / B''s model' /")

    assert [(token.text, token.kind, token.quoted) for token in tokens] == [
        ("TITLE", GrdeclTokenKind.VALUE, False),
        ("A / B's model", GrdeclTokenKind.VALUE, True),
        ("/", GrdeclTokenKind.TERMINATOR, False),
    ]


def test_grdecl_parser_rejects_unterminated_records_and_malformed_numbers() -> None:
    parser = GrdeclParser()

    with pytest.raises(ParseError, match="Unterminated keyword"):
        parser.parse_text("PORO 1 2 3")

    with pytest.raises(ParseError, match="Invalid numeric"):
        parser.parse_text("PORO 1.2.3 /")

    with pytest.raises(ParseError, match="Unexpected '/'"):
        parser.parse_text("/")


def test_grdecl_reader_reads_text_files_and_reports_missing_files(tmp_path: Path) -> None:
    path = tmp_path / "CASE.GRDECL"
    path.write_text("PORO 2*0.2 /", encoding="utf-8")

    dataset = GrdeclReader().read(path)

    assert dataset.source == str(path)
    assert dataset.record("PORO").values == (0.2, 0.2)

    with pytest.raises(FileReadError):
        GrdeclReader().read(tmp_path / "MISSING.GRDECL")
