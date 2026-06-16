"""User-facing simulation case object."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Sequence, Union

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import LoadCaseOptions

CasePath = Union[str, Path]


@dataclass(frozen=True, slots=True)
class SimulationCase:
    """Represents one discovered simulation case without eagerly loading payloads."""

    case_name: str
    root_path: Path
    manifest: CaseManifest
    options: LoadCaseOptions

    @classmethod
    def open(
        cls, path_or_basename: CasePath, options: LoadCaseOptions | None = None
    ) -> "SimulationCase":
        """Open a case by basename, file path, or unambiguous directory."""

        from reservoir_data.application.case_loader import CaseLoader

        return CaseLoader().load(path_or_basename, options)

    def available_data(self) -> tuple[FileCategory, ...]:
        """Return discovered data categories without loading payloads."""

        return self.manifest.available_categories()

    def has_data(self, category: FileCategory) -> bool:
        """Return whether the manifest contains a data category."""

        return self.manifest.has_category(category)

    def files_for(self, category: FileCategory) -> tuple[FormatDetectionResult, ...]:
        """Return detected files for a data category."""

        return self.manifest.files_for(category)

    def load_grid(self) -> NoReturn:
        self._require_category(FileCategory.GRID, "grid")
        self._unsupported("GRID/EGRID grid loading")

    def load_properties(self, names: Sequence[str] | None = None) -> NoReturn:
        del names
        self._require_category(FileCategory.INIT, "initialization/property")
        self._unsupported("INIT/property loading")

    def load_restarts(self) -> NoReturn:
        self._require_category(FileCategory.RESTART, "restart")
        self._unsupported("restart loading")

    def load_summary(self) -> NoReturn:
        if not (
            self.has_data(FileCategory.SUMMARY_METADATA)
            or self.has_data(FileCategory.SUMMARY_DATA)
        ):
            raise FileReadError(
                f"No summary files were discovered for case '{self.case_name}'"
            )
        self._unsupported("summary loading")

    def load_wells(self, load_segments: bool = True) -> NoReturn:
        del load_segments
        self._require_category(FileCategory.RESTART, "restart well")
        self._unsupported("well timeline extraction")

    def load_rft(self) -> NoReturn:
        if not (self.has_data(FileCategory.RFT) or self.has_data(FileCategory.PLT)):
            raise FileReadError(
                f"No RFT/PLT files were discovered for case '{self.case_name}'"
            )
        self._unsupported("RFT/PLT loading")

    def _require_category(self, category: FileCategory, label: str) -> None:
        if not self.has_data(category):
            raise FileReadError(
                f"No {label} files were discovered for case '{self.case_name}'"
            )

    def _unsupported(self, workflow: str) -> NoReturn:
        raise UnsupportedFormatError(
            f"{workflow} is not implemented yet. Discovery found matching files, "
            "but this milestone does not parse file payloads."
        )
