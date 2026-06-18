from datetime import date
from pathlib import Path

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import ParseError
from reservoir_data.formats.deck import FormattedDeckReader
from reservoir_data.public import DeckMetadata
from reservoir_data.public.case_facade import SimulationCase


def test_formatted_deck_reader_extracts_title_start_and_keywords(
    tmp_path: Path,
) -> None:
    path = tmp_path / "CASE.DATA"
    path.write_text(
        """
        TITLE 'Small model' /
        START 1 JAN 2026 /
        GRID /
        """,
        encoding="utf-8",
    )

    metadata = FormattedDeckReader().read(path)

    assert isinstance(metadata, DeckMetadata)
    assert metadata.title == "Small model"
    assert metadata.start_date == date(2026, 1, 1)
    assert metadata.keyword_names == ("TITLE", "START", "GRID")
    assert metadata.has_keyword("grid")
    assert metadata.keyword_count() == 3
    assert metadata.keyword_count("grid") == 1
    assert metadata.unique_keyword_names() == ("TITLE", "START", "GRID")
    assert metadata.source == str(path)


def test_deck_metadata_counts_duplicate_keywords() -> None:
    metadata = DeckMetadata(keyword_names=("TITLE", "GRID", "GRID", "PROPS"))

    assert metadata.keyword_count() == 4
    assert metadata.keyword_count("grid") == 2
    assert metadata.unique_keyword_names() == ("TITLE", "GRID", "PROPS")


def test_formatted_deck_reader_accepts_iso_start_string(tmp_path: Path) -> None:
    path = tmp_path / "CASE.DATA"
    path.write_text("START '2026-03-04' /", encoding="utf-8")

    metadata = FormattedDeckReader().read(path)

    assert metadata.title is None
    assert metadata.start_date == date(2026, 3, 4)


def test_public_case_loads_deck_metadata(tmp_path: Path) -> None:
    (tmp_path / "CASE.DATA").write_text(
        "TITLE 'Public case' / START 2026 2 3 /",
        encoding="utf-8",
    )

    case = SimulationCase.open(tmp_path / "CASE")
    metadata = case.load_deck_metadata()

    assert FileCategory.DECK in case.available_data()
    assert metadata.title == "Public case"
    assert metadata.start_date == date(2026, 2, 3)


def test_formatted_deck_reader_rejects_malformed_start(tmp_path: Path) -> None:
    path = tmp_path / "CASE.DATA"
    path.write_text("START 2026 /", encoding="utf-8")

    with pytest.raises(ParseError, match="START"):
        FormattedDeckReader().read(path)
