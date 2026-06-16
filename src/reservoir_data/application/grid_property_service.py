"""Application service for grid and INIT/property workflows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.exceptions.errors import FileReadError
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.init.init_reader import InitReader
from reservoir_data.schemas.loading import FormattedFilePreference


@dataclass(frozen=True, slots=True)
class GridPropertyService:
    """Coordinate grid and initialization property loading."""

    grid_reader: GridReader = field(default_factory=GridReader)
    init_reader: InitReader = field(default_factory=InitReader)

    def load_grid(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> ReservoirGrid:
        """Load the preferred supported grid file."""

        detection = manifest.preferred_file(FileCategory.GRID, preference)
        if detection is None:
            raise FileReadError(
                f"No grid file was discovered for case '{manifest.case_name}'"
            )
        return self.grid_reader.read(detection.path)

    def load_properties(
        self,
        manifest: CaseManifest,
        names: Sequence[str] | None = None,
        grid: ReservoirGrid | None = None,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> PropertyCollection:
        """Load selected initialization properties."""

        detection = manifest.preferred_file(FileCategory.INIT, preference)
        if detection is None:
            raise FileReadError(
                f"No initialization/property file was discovered for case "
                f"'{manifest.case_name}'"
            )
        return self.init_reader.read(detection.path, grid=grid, names=names)
