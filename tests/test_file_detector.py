from __future__ import annotations

from pathlib import Path
import unittest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import UnsupportedFormatError
from reservoir_data.infrastructure.filesystem.file_detector import FileDetector


class FileDetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = FileDetector()

    def test_detects_known_case_file_extensions(self) -> None:
        cases = {
            "CASE.DATA": (FileCategory.DECK, True, None),
            "CASE.GRDECL": (FileCategory.GRDECL, True, None),
            "CASE.EGRID": (FileCategory.GRID, False, None),
            "CASE.FGRID": (FileCategory.GRID, True, None),
            "CASE.INIT": (FileCategory.INIT, False, None),
            "CASE.UNRST": (FileCategory.RESTART, False, True),
            "CASE.FUNRST": (FileCategory.RESTART, True, True),
            "CASE.SMSPEC": (FileCategory.SUMMARY_SPEC, None, None),
            "CASE.UNSMRY": (FileCategory.SUMMARY_DATA, False, True),
            "CASE.RFT": (FileCategory.RFT, None, None),
        }

        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                result = self.detector.detect(Path(filename))
                self.assertEqual(result.file_category, expected[0])
                self.assertEqual(result.formatted, expected[1])
                self.assertEqual(result.unified, expected[2])
                self.assertTrue(result.is_known)

    def test_detection_is_case_insensitive(self) -> None:
        result = self.detector.detect("case.egrid")

        self.assertEqual(result.file_category, FileCategory.GRID)
        self.assertFalse(result.formatted)

    def test_detects_non_unified_restart_report_step(self) -> None:
        result = self.detector.detect("CASE.X0012")

        self.assertEqual(result.file_category, FileCategory.RESTART)
        self.assertFalse(result.formatted)
        self.assertFalse(result.unified)
        self.assertEqual(result.report_step, 12)
        self.assertLess(result.confidence, 1.0)

    def test_detects_formatted_non_unified_restart_report_step(self) -> None:
        result = self.detector.detect("CASE.F0034")

        self.assertEqual(result.file_category, FileCategory.RESTART)
        self.assertTrue(result.formatted)
        self.assertFalse(result.unified)
        self.assertEqual(result.report_step, 34)

    def test_detects_non_unified_summary_report_step(self) -> None:
        result = self.detector.detect("CASE.S0007")

        self.assertEqual(result.file_category, FileCategory.SUMMARY_DATA)
        self.assertFalse(result.formatted)
        self.assertFalse(result.unified)
        self.assertEqual(result.report_step, 7)

    def test_unknown_extension_is_non_strict_unknown(self) -> None:
        result = self.detector.detect("CASE.TXT")

        self.assertEqual(result.file_category, FileCategory.UNKNOWN)
        self.assertFalse(result.is_known)
        self.assertEqual(result.confidence, 0.0)
        self.assertTrue(result.diagnostics)

    def test_unknown_extension_is_strict_error(self) -> None:
        with self.assertRaises(UnsupportedFormatError):
            self.detector.detect("CASE.TXT", strict=True)


if __name__ == "__main__":
    unittest.main()
