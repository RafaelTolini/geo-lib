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
