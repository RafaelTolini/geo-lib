import pytest

from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.keyword.keyword_record import KeywordRecord
from reservoir_data.domain.keyword.keyword_type import KeywordType
from reservoir_data.exceptions.errors import (
    AmbiguousKeywordError,
    MissingKeywordError,
    UnsupportedFormatError,
)
from reservoir_data.schemas.queries import CaseSensitivity, KeywordQuery


def test_keyword_dataset_queries_by_name_and_occurrence() -> None:
    dataset = KeywordDataset(
        records=(
            KeywordRecord.from_values("PORO", [0.1, 0.2]),
            KeywordRecord.from_values("PERMX", [10, 20]),
            KeywordRecord.from_values("PORO", [0.3, 0.4]),
        )
    )

    assert dataset.names() == ("PORO", "PERMX", "PORO")
    assert dataset.has_keyword("poro")
    assert dataset.record("PORO", occurrence_index=1).values == (0.3, 0.4)
    assert dataset.record("MISSING", required=False) is None
    assert dataset.filtered("poro").names() == ("PORO", "PORO")
    assert dataset.unique_names() == ("PORO", "PERMX")
    assert dataset.keyword_count() == 3
    assert dataset.keyword_count("poro") == 2


def test_keyword_dataset_exports_metadata_rows(tmp_path) -> None:
    path = tmp_path / "keywords.csv"
    dataset = KeywordDataset(
        records=(
            KeywordRecord.from_values("PORO", [0.1, 0.2]),
            KeywordRecord.from_values("PORO", [0.3]),
        ),
        source="CASE.DATA",
    )

    rows = dataset.rows()
    dataset.to_csv(path)

    assert rows[1]["KEYWORD"] == "PORO"
    assert rows[1]["OCCURRENCE_INDEX"] == 1
    assert rows[1]["VALUE_COUNT"] == 1
    assert "INDEX,KEYWORD,OCCURRENCE_INDEX,TYPE,VALUE_COUNT,SOURCE" in (
        path.read_text(encoding="utf-8")
    )


def test_keyword_query_validates_type_size_and_case_policy() -> None:
    dataset = KeywordDataset(
        records=(KeywordRecord.from_values("Title", ["CASE A"]),)
    )

    insensitive = dataset.query(
        KeywordQuery(
            keyword_name="title",
            expected_type=KeywordType.STRING,
            expected_size=1,
        )
    )

    assert insensitive is not None
    assert insensitive.scalar() == "CASE A"
    assert not dataset.has_keyword("title", CaseSensitivity.SENSITIVE)


def test_keyword_query_reports_missing_ambiguous_and_type_mismatch() -> None:
    dataset = KeywordDataset(
        records=(
            KeywordRecord.from_values("PORO", [0.1]),
            KeywordRecord.from_values("PORO", [0.2]),
        )
    )

    with pytest.raises(AmbiguousKeywordError):
        dataset.query(KeywordQuery("PORO", occurrence_index=None))

    with pytest.raises(MissingKeywordError):
        dataset.query(KeywordQuery("PERMX"))

    with pytest.raises(UnsupportedFormatError):
        dataset.query(KeywordQuery("PORO", expected_type=KeywordType.INTEGER))

    with pytest.raises(ValueError):
        dataset.query(KeywordQuery("PORO", expected_size=2))


def test_keyword_dataset_returns_contiguous_blocks() -> None:
    dataset = KeywordDataset(
        records=(
            KeywordRecord.from_values("RUNSPEC", []),
            KeywordRecord.from_values("GRID", []),
            KeywordRecord.from_values("SPECGRID", [1, 1, 1]),
            KeywordRecord.from_values("PROPS", []),
            KeywordRecord.from_values("PORO", [0.2]),
            KeywordRecord.from_values("SOLUTION", []),
        ),
        source="CASE.DATA",
    )

    grid_block = dataset.block("GRID", "PROPS", include_boundaries=False)
    solution_block = dataset.block("PROPS")

    assert grid_block.names() == ("SPECGRID",)
    assert grid_block.source == "CASE.DATA"
    assert solution_block.names() == ("PROPS", "PORO", "SOLUTION")


def test_keyword_dataset_block_respects_occurrence_and_errors() -> None:
    dataset = KeywordDataset(
        records=(
            KeywordRecord.from_values("DATES", ["2026-01-01"]),
            KeywordRecord.from_values("WELSPECS", ["A"]),
            KeywordRecord.from_values("DATES", ["2026-02-01"]),
            KeywordRecord.from_values("WELSPECS", ["B"]),
        )
    )

    assert dataset.block(
        "DATES",
        "WELSPECS",
        start_occurrence_index=1,
        end_occurrence_index=1,
    ).names() == ("DATES", "WELSPECS")

    with pytest.raises(MissingKeywordError):
        dataset.block("NOPE")
    with pytest.raises(ValueError, match="before"):
        dataset.block("WELSPECS", "DATES")
