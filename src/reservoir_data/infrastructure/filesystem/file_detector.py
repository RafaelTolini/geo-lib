"""Case-file type detection from conservative filename conventions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import UnsupportedFormatError
from reservoir_data.schemas.detection import FormatDetectionResult


_KNOWN_SUFFIXES: dict[str, tuple[FileCategory, bool | None, bool | None, tuple[str, ...]]] = {
    ".DATA": (FileCategory.DECK, True, None, ()),
    ".GRDECL": (FileCategory.GRDECL, True, None, ()),
    ".GRID": (FileCategory.GRID, False, None, ()),
    ".EGRID": (FileCategory.GRID, False, None, ()),
    ".FGRID": (
        FileCategory.GRID,
        True,
        None,
        ("Formatted GRID extension inferred; exact simulator conventions require verification.",),
    ),
    ".FEGRID": (
        FileCategory.GRID,
        True,
        None,
        ("Formatted EGRID extension inferred; exact simulator conventions require verification.",),
    ),
    ".INIT": (FileCategory.INIT, False, None, ()),
    ".FINIT": (
        FileCategory.INIT,
        True,
        None,
        ("Formatted INIT extension inferred; exact simulator conventions require verification.",),
    ),
    ".UNRST": (FileCategory.RESTART, False, True, ()),
    ".FUNRST": (
        FileCategory.RESTART,
        True,
        True,
        ("Formatted unified restart extension inferred; exact simulator conventions require verification.",),
    ),
    ".SMSPEC": (FileCategory.SUMMARY_SPEC, None, None, ()),
    ".FSMSPEC": (
        FileCategory.SUMMARY_SPEC,
        True,
        None,
        ("Formatted SMSPEC extension inferred; exact simulator conventions require verification.",),
    ),
    ".UNSMRY": (FileCategory.SUMMARY_DATA, False, True, ()),
    ".FUNSMRY": (
        FileCategory.SUMMARY_DATA,
        True,
        True,
        ("Formatted unified summary extension inferred; exact simulator conventions require verification.",),
    ),
    ".RFT": (FileCategory.RFT, None, None, ()),
    ".FRFT": (
        FileCategory.RFT,
        True,
        None,
        ("Formatted RFT extension inferred; exact simulator conventions require verification.",),
    ),
}

_NON_UNIFIED_RESTART_SUFFIX = re.compile(r"^\.(?P<prefix>X|F)(?P<step>\d{4,})$")
_NON_UNIFIED_SUMMARY_SUFFIX = re.compile(r"^\.(?P<prefix>S)(?P<step>\d{4,})$")


@dataclass(frozen=True, slots=True)
class FileDetector:
    """Detect a file role from its extension without reading payload data."""

    def detect(self, path: str | Path, *, strict: bool = False) -> FormatDetectionResult:
        """Detect a supported file category from a path."""

        candidate = Path(path)
        suffix = candidate.suffix.upper()
        if suffix in _KNOWN_SUFFIXES:
            category, formatted, unified, diagnostics = _KNOWN_SUFFIXES[suffix]
            return FormatDetectionResult(
                path=candidate,
                file_category=category,
                formatted=formatted,
                unified=unified,
                confidence=1.0,
                diagnostics=diagnostics,
            )

        restart_match = _NON_UNIFIED_RESTART_SUFFIX.match(suffix)
        if restart_match is not None:
            prefix = restart_match.group("prefix")
            return FormatDetectionResult(
                path=candidate,
                file_category=FileCategory.RESTART,
                formatted=prefix == "F",
                unified=False,
                report_step=int(restart_match.group("step")),
                confidence=0.85,
                diagnostics=(
                    "Non-unified restart report-step inferred from extension; "
                    "exact conventions require independent verification.",
                ),
            )

        summary_match = _NON_UNIFIED_SUMMARY_SUFFIX.match(suffix)
        if summary_match is not None:
            return FormatDetectionResult(
                path=candidate,
                file_category=FileCategory.SUMMARY_DATA,
                formatted=False,
                unified=False,
                report_step=int(summary_match.group("step")),
                confidence=0.85,
                diagnostics=(
                    "Non-unified summary report-step inferred from extension; "
                    "exact conventions require independent verification.",
                ),
            )

        message = f"Unsupported reservoir data extension for {candidate.name!r}"
        if strict:
            raise UnsupportedFormatError(message)
        return FormatDetectionResult(
            path=candidate,
            file_category=FileCategory.UNKNOWN,
            confidence=0.0,
            diagnostics=(message,),
        )
