"""Application service for deck metadata loading."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.deck import DeckMetadata
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.formats.deck import FormattedDeckReader
from reservoir_data.schemas.loading import FormattedFilePreference


@dataclass(frozen=True, slots=True)
class DeckService:
    """Coordinate deck metadata loading from a discovered case manifest."""

    formatted_reader: FormattedDeckReader = FormattedDeckReader()

    def load_metadata(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> DeckMetadata:
        """Load externally useful `.DATA` deck metadata."""

        detection = manifest.preferred_file(FileCategory.DECK, preference)
        if detection is None:
            raise FileReadError(
                f"No deck files were discovered for case '{manifest.case_name}'"
            )
        if detection.formatted is False:
            raise UnsupportedFormatError(
                f"Deck file {detection.path} is not a supported formatted text deck"
            )
        return self.formatted_reader.read(detection.path)
