from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import (
    FileDetectionError,
    FileReadError,
    UnsupportedFormatError,
)
from reservoir_data.public.case_facade import SimulationCase
from reservoir_data.schemas.loading import LoadCaseOptions


class CaseDiscoveryTests(unittest.TestCase):
    def test_open_discovers_case_files_without_loading_payloads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._touch(root, "CASE.DATA")
            self._touch(root, "CASE.EGRID")
            self._touch(root, "CASE.INIT")
            self._touch(root, "CASE.UNRST")
            self._touch(root, "CASE.X0004")
            self._touch(root, "CASE.SMSPEC")
            self._touch(root, "CASE.UNSMRY")
            self._touch(root, "CASE.RFT")

            case = SimulationCase.open(root / "CASE")

            self.assertEqual(case.name, "CASE")
            self.assertEqual(
                case.available_data(),
                ("deck", "grid", "properties", "restart", "summary", "rft"),
            )
            self.assertTrue(case.has_data(FileCategory.GRID))
            self.assertEqual(
                case.manifest.preferred_file(FileCategory.RESTART).path.name,
                "CASE.UNRST",
            )
            self.assertIn("Multiple restart files discovered", " ".join(case.manifest.diagnostics))

    def test_category_filter_limits_discovery(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._touch(root, "CASE.DATA")
            self._touch(root, "CASE.EGRID")
            options = LoadCaseOptions.with_category_filters([FileCategory.GRID])

            case = SimulationCase.open(root / "CASE", options)

            self.assertEqual(case.available_data(), ("grid",))
            self.assertFalse(case.has_data(FileCategory.DECK))
            self.assertTrue(case.has_data(FileCategory.GRID))

    def test_dotted_case_basename_is_not_treated_as_missing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._touch(root, "MODEL.V1.DATA")

            case = SimulationCase.open(root / "MODEL.V1")

            self.assertEqual(case.name, "MODEL.V1")
            self.assertEqual(case.available_data(), ("deck",))

    def test_strict_discovery_errors_when_no_files_match(self) -> None:
        with TemporaryDirectory() as tmp:
            options = LoadCaseOptions(strict_discovery=True)

            with self.assertRaises(FileDetectionError):
                SimulationCase.open(Path(tmp) / "CASE", options)

    def test_non_strict_discovery_allows_empty_manifest(self) -> None:
        with TemporaryDirectory() as tmp:
            case = SimulationCase.open(Path(tmp) / "CASE")

            self.assertEqual(case.available_data(), ())
            self.assertEqual(case.name, "CASE")

    def test_explicit_missing_file_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileReadError):
                SimulationCase.open(Path(tmp) / "CASE.DATA")

    def test_strict_discovery_rejects_unsupported_matching_extension(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._touch(root, "CASE.TXT")
            options = LoadCaseOptions(strict_discovery=True)

            with self.assertRaises(UnsupportedFormatError):
                SimulationCase.open(root / "CASE", options)

    def test_loader_methods_are_explicitly_unsupported_until_readers_exist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._touch(root, "CASE.EGRID")
            self._touch(root, "CASE.SMSPEC")

            case = SimulationCase.open(root / "CASE")

            with self.assertRaises(UnsupportedFormatError):
                case.load_grid()
            with self.assertRaises(UnsupportedFormatError):
                case.load_summary()
            with self.assertRaises(FileDetectionError):
                case.load_rft()

    @staticmethod
    def _touch(root: Path, name: str) -> None:
        (root / name).write_text("", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
