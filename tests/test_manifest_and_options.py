from __future__ import annotations

from pathlib import Path
import unittest

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import (
    FileDetectionError,
    GridGeometryError,
    InvalidCellIndexError,
    ReservoirDataError,
    SummaryDataError,
)
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import CachePolicy, FormatPreference, LoadCaseOptions


class ManifestAndOptionsTests(unittest.TestCase):
    def test_exception_taxonomy_uses_base_error(self) -> None:
        for error_type in (
            FileDetectionError,
            GridGeometryError,
            InvalidCellIndexError,
            SummaryDataError,
        ):
            with self.subTest(error_type=error_type.__name__):
                self.assertTrue(issubclass(error_type, ReservoirDataError))

    def test_load_case_options_normalize_enum_inputs(self) -> None:
        options = LoadCaseOptions(
            preferred_format="formatted",
            cache_policy="read_write",
            file_category_filters=frozenset({"grid", "restart"}),
        )

        self.assertEqual(options.preferred_format, FormatPreference.FORMATTED)
        self.assertEqual(options.cache_policy, CachePolicy.READ_WRITE)
        self.assertTrue(options.allows_category(FileCategory.GRID))
        self.assertFalse(options.allows_category(FileCategory.RFT))

    def test_detection_result_validates_confidence(self) -> None:
        with self.assertRaises(ValueError):
            FormatDetectionResult(
                path=Path("CASE.DATA"),
                file_category=FileCategory.DECK,
                confidence=1.5,
            )

    def test_manifest_maps_public_data_names(self) -> None:
        manifest = CaseManifest(
            case_name="CASE",
            root_path=Path("."),
            files_by_category={
                FileCategory.INIT: (
                    FormatDetectionResult(Path("CASE.INIT"), FileCategory.INIT),
                ),
                FileCategory.SUMMARY_SPEC: (
                    FormatDetectionResult(Path("CASE.SMSPEC"), FileCategory.SUMMARY_SPEC),
                ),
                FileCategory.SUMMARY_DATA: (
                    FormatDetectionResult(Path("CASE.UNSMRY"), FileCategory.SUMMARY_DATA),
                ),
            },
        )

        self.assertEqual(manifest.available_data(), ("properties", "summary"))

    def test_manifest_preferred_file_errors_when_missing(self) -> None:
        manifest = CaseManifest(case_name="CASE", root_path=Path("."), files_by_category={})

        with self.assertRaises(FileDetectionError):
            manifest.preferred_file(FileCategory.GRID)


if __name__ == "__main__":
    unittest.main()
