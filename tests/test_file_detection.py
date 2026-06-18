from pathlib import Path

import pytest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError
from reservoir_data.formats.common.file_detector import FileDetector


@pytest.mark.parametrize(
    ("filename", "category", "formatted", "unified", "report_step"),
    [
        ("CASE.DATA", FileCategory.DECK, True, None, None),
        ("CASE.GRDECL", FileCategory.GRDECL, True, None, None),
        ("CASE.EGRID", FileCategory.GRID, None, None, None),
        ("CASE.FGRID", FileCategory.GRID, True, None, None),
        ("CASE.INIT", FileCategory.INIT, None, None, None),
        ("CASE.UNRST", FileCategory.RESTART, False, True, None),
        ("CASE.FUNRST", FileCategory.RESTART, True, True, None),
        ("CASE.X0012", FileCategory.RESTART, False, False, 12),
        ("CASE.F0012", FileCategory.RESTART, True, False, 12),
        ("CASE.SMSPEC", FileCategory.SUMMARY_METADATA, None, None, None),
        ("CASE.UNSMRY", FileCategory.SUMMARY_DATA, False, True, None),
        ("CASE.S0003", FileCategory.SUMMARY_DATA, False, False, 3),
        ("CASE.A0003", FileCategory.SUMMARY_DATA, True, False, 3),
        ("CASE.RFT", FileCategory.RFT, None, None, None),
        ("CASE.PLT", FileCategory.PLT, None, None, None),
    ],
)
def test_file_detector_recognizes_supported_filename_patterns(
    filename: str,
    category: FileCategory,
    formatted: bool | None,
    unified: bool | None,
    report_step: int | None,
) -> None:
    result = FileDetector().detect(Path(filename))

    assert result.file_category == category
    assert result.formatted is formatted
    assert result.unified is unified
    assert result.report_step == report_step
    assert result.confidence > 0.0
    assert result.diagnostics
    row = result.to_row()
    assert row["FILE_NAME"] == filename
    assert row["CATEGORY"] == category.value
    assert row["FORMAT"] == result.format_label


def test_file_detector_rejects_unknown_extension() -> None:
    with pytest.raises(FileDetectionError):
        FileDetector().detect(Path("CASE.UNKNOWN"))
