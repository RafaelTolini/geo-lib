"""Filename-based format detection for reservoir simulation files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError
from reservoir_data.schemas.detection import FormatDetectionResult


@dataclass(frozen=True, slots=True)
class FileDetector:
    """Detect recognized reservoir data file categories from filenames."""

    _NON_UNIFIED_RESTART: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<prefix>[XF])(?P<step>\d{4,})$"
    )
    _NON_UNIFIED_SUMMARY: ClassVar[re.Pattern[str]] = re.compile(
        r"^(?P<prefix>[SA])(?P<step>\d{4,})$"
    )

    def detect(self, path: str | Path) -> FormatDetectionResult:
        """Return a detection result based on the file extension.

        This milestone intentionally performs filename detection only. It does
        not inspect or parse payload bytes.
        """

        candidate = Path(path)
        extension = candidate.suffix[1:].upper()
        if not extension:
            raise FileDetectionError(f"File has no extension: {candidate}")

        static_result = self._detect_static_extension(candidate, extension)
        if static_result is not None:
            return static_result

        step_result = self._detect_non_unified_step(candidate, extension)
        if step_result is not None:
            return step_result

        raise FileDetectionError(f"Unrecognized reservoir data extension: .{extension}")

    def _detect_static_extension(
        self, path: Path, extension: str
    ) -> FormatDetectionResult | None:
        static_extensions: dict[
            str, tuple[FileCategory, bool | None, bool | None, tuple[str, ...]]
        ] = {
            "DATA": (
                FileCategory.DECK,
                True,
                None,
                ("Detected deck file from extension.",),
            ),
            "GRDECL": (
                FileCategory.GRDECL,
                True,
                None,
                ("Detected GRDECL text keyword file from extension.",),
            ),
            "GRID": (
                FileCategory.GRID,
                None,
                None,
                ("Detected GRID geometry file from extension.",),
            ),
            "FGRID": (
                FileCategory.GRID,
                True,
                None,
                ("Detected formatted GRID geometry file from extension.",),
            ),
            "EGRID": (
                FileCategory.GRID,
                None,
                None,
                ("Detected EGRID geometry file from extension.",),
            ),
            "FEGRID": (
                FileCategory.GRID,
                True,
                None,
                ("Detected formatted EGRID geometry file from extension.",),
            ),
            "INIT": (
                FileCategory.INIT,
                None,
                None,
                ("Detected INIT property file from extension.",),
            ),
            "FINIT": (
                FileCategory.INIT,
                True,
                None,
                ("Detected formatted INIT property file from extension.",),
            ),
            "UNRST": (
                FileCategory.RESTART,
                False,
                True,
                ("Detected unified restart file from extension.",),
            ),
            "FUNRST": (
                FileCategory.RESTART,
                True,
                True,
                ("Detected formatted unified restart file from extension.",),
            ),
            "SMSPEC": (
                FileCategory.SUMMARY_METADATA,
                None,
                None,
                ("Detected summary metadata file from extension.",),
            ),
            "FSMSPEC": (
                FileCategory.SUMMARY_METADATA,
                True,
                None,
                ("Detected formatted summary metadata file from extension.",),
            ),
            "UNSMRY": (
                FileCategory.SUMMARY_DATA,
                False,
                True,
                ("Detected unified summary data file from extension.",),
            ),
            "FUNSMRY": (
                FileCategory.SUMMARY_DATA,
                True,
                True,
                ("Detected formatted unified summary data file from extension.",),
            ),
            "RFT": (
                FileCategory.RFT,
                None,
                None,
                ("Detected RFT measurement file from extension.",),
            ),
            "FRFT": (
                FileCategory.RFT,
                True,
                None,
                ("Detected formatted RFT measurement file from extension.",),
            ),
            "PLT": (
                FileCategory.PLT,
                None,
                None,
                ("Detected PLT measurement file from extension.",),
            ),
            "FPLT": (
                FileCategory.PLT,
                True,
                None,
                ("Detected formatted PLT measurement file from extension.",),
            ),
        }

        detected = static_extensions.get(extension)
        if detected is None:
            return None

        category, formatted, unified, diagnostics = detected
        return FormatDetectionResult(
            path=path,
            file_category=category,
            formatted=formatted,
            unified=unified,
            report_step=None,
            confidence=0.95,
            diagnostics=diagnostics,
        )

    def _detect_non_unified_step(
        self, path: Path, extension: str
    ) -> FormatDetectionResult | None:
        restart_match = self._NON_UNIFIED_RESTART.match(extension)
        if restart_match is not None:
            prefix = restart_match.group("prefix")
            step = int(restart_match.group("step"))
            formatted = prefix == "F"
            return FormatDetectionResult(
                path=path,
                file_category=FileCategory.RESTART,
                formatted=formatted,
                unified=False,
                report_step=step,
                confidence=0.75,
                diagnostics=(
                    "Detected non-unified restart report-step file from extension.",
                    "Exact simulator naming conventions require independent verification.",
                ),
            )

        summary_match = self._NON_UNIFIED_SUMMARY.match(extension)
        if summary_match is not None:
            prefix = summary_match.group("prefix")
            step = int(summary_match.group("step"))
            formatted = prefix == "A"
            return FormatDetectionResult(
                path=path,
                file_category=FileCategory.SUMMARY_DATA,
                formatted=formatted,
                unified=False,
                report_step=step,
                confidence=0.70,
                diagnostics=(
                    "Detected non-unified summary data file from extension.",
                    "Exact simulator naming conventions require independent verification.",
                ),
            )

        return None
