"""Application service for RFT/PLT workflows."""

from __future__ import annotations

from dataclasses import dataclass, field

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.rft.rft_dataset import RftDataset
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.formats.rft.formatted_rft_reader import FormattedRftReader
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.loading import FormattedFilePreference


@dataclass(frozen=True, slots=True)
class RftService:
    """Coordinate formatted RFT/PLT loading from a case manifest."""

    rft_reader: FormattedRftReader = field(default_factory=FormattedRftReader)

    def load_rft(
        self,
        manifest: CaseManifest,
        grid: ReservoirGrid | None = None,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> RftDataset:
        """Load supported formatted RFT/PLT records."""

        detections = self._select_supported_detections(manifest, preference)
        return self.rft_reader.read(detections, grid=grid)

    def _select_supported_detections(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference,
    ) -> tuple[FormatDetectionResult, ...]:
        detections = (
            *manifest.files_for(FileCategory.RFT),
            *manifest.files_for(FileCategory.PLT),
        )
        if not detections:
            raise FileReadError(
                f"No RFT/PLT files were discovered for case '{manifest.case_name}'"
            )

        normalized_preference = FormattedFilePreference(preference)
        if normalized_preference is FormattedFilePreference.UNFORMATTED:
            raise UnsupportedFormatError(
                "Unformatted RFT/PLT decoding is not implemented"
            )

        formatted = tuple(
            detection for detection in detections if detection.formatted is True
        )
        if not formatted:
            raise UnsupportedFormatError(
                "Only formatted RFT/PLT files are supported by the current reader"
            )
        return tuple(sorted(formatted, key=lambda item: item.path.name.casefold()))
