"""Public case facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Sequence

from reservoir_data.application.case_loader import CaseLoader
from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileDetectionError, UnsupportedFormatError
from reservoir_data.schemas.loading import LoadCaseOptions


@dataclass(frozen=True, slots=True)
class SimulationCase:
    """User-facing object representing one discovered simulation case."""

    name: str | None
    root_path: Path
    manifest: CaseManifest
    options: LoadCaseOptions

    @classmethod
    def open(
        cls,
        path_or_basename: str | Path,
        options: LoadCaseOptions | None = None,
    ) -> "SimulationCase":
        """Discover a case without eagerly loading data files."""

        load_options = options or LoadCaseOptions()
        manifest = CaseLoader().load_manifest(path_or_basename, load_options)
        return cls(
            name=manifest.case_name,
            root_path=manifest.root_path,
            manifest=manifest,
            options=load_options,
        )

    def available_data(self) -> tuple[str, ...]:
        """Return user-facing data categories discovered for this case."""

        return self.manifest.available_data()

    def has_data(self, category: FileCategory | str) -> bool:
        """Return whether a file category was discovered."""

        return self.manifest.has_category(category)

    def load_grid(self) -> NoReturn:
        """Load a grid when a real grid reader is implemented."""

        self._unsupported_until_reader_exists(FileCategory.GRID, "GRID/EGRID reader")

    def load_properties(self, names: Sequence[str] | None = None) -> NoReturn:
        """Load initialization properties when a real INIT reader is implemented."""

        del names
        self._unsupported_until_reader_exists(FileCategory.INIT, "INIT/property reader")

    def load_restarts(self) -> NoReturn:
        """Load restart data when a real restart reader is implemented."""

        self._unsupported_until_reader_exists(FileCategory.RESTART, "restart reader")

    def load_summary(self) -> NoReturn:
        """Load summary data when real summary readers are implemented."""

        if not (
            self.manifest.has_category(FileCategory.SUMMARY_SPEC)
            or self.manifest.has_category(FileCategory.SUMMARY_DATA)
        ):
            raise FileDetectionError("No summary files were discovered for this case")
        raise UnsupportedFormatError(
            "Summary parsing is not implemented in milestone M1; discovery found summary files only."
        )

    def load_wells(self, load_segments: bool = True) -> NoReturn:
        """Load well data when restart well extraction is implemented."""

        del load_segments
        self._unsupported_until_reader_exists(FileCategory.RESTART, "well-data restart extraction")

    def load_rft(self) -> NoReturn:
        """Load RFT/PLT data when a real RFT/PLT reader is implemented."""

        self._unsupported_until_reader_exists(FileCategory.RFT, "RFT/PLT reader")

    def _unsupported_until_reader_exists(
        self,
        category: FileCategory,
        reader_name: str,
    ) -> NoReturn:
        if not self.manifest.has_category(category):
            raise FileDetectionError(f"No {category.public_data_name} files were discovered for this case")
        raise UnsupportedFormatError(
            f"{reader_name} is not implemented in milestone M1; discovery found files only."
        )
