"""Application service for grid and INIT/property workflows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.formats.grid.grid_reader import GridReader
from reservoir_data.formats.init.init_reader import InitReader
from reservoir_data.schemas.loading import (
    FormattedFilePreference,
    GeometryValidationLevel,
    GridLoadOptions,
)


@dataclass(frozen=True, slots=True)
class GridPropertyService:
    """Coordinate grid and initialization property loading."""

    grid_reader: GridReader = field(default_factory=GridReader)
    init_reader: InitReader = field(default_factory=InitReader)

    def load_grid(
        self,
        manifest: CaseManifest,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
        options: GridLoadOptions | None = None,
    ) -> ReservoirGrid:
        """Load the preferred supported grid file."""

        self._validate_grid_options(options or GridLoadOptions())
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
        lazy: bool = True,
    ) -> PropertyCollection:
        """Load selected initialization properties."""

        detection = manifest.preferred_file(FileCategory.INIT, preference)
        if detection is None:
            raise FileReadError(
                f"No initialization/property file was discovered for case "
                f"'{manifest.case_name}'"
            )
        return self.init_reader.read(
            detection.path,
            grid=grid,
            names=names,
            lazy=lazy,
        )

    def _validate_grid_options(self, options: GridLoadOptions) -> None:
        if options.apply_coordinate_transforms:
            raise UnsupportedFormatError(
                "Coordinate transform application is not implemented for grid loading"
            )
        if options.load_local_grids:
            raise UnsupportedFormatError("Local grid loading is not implemented")
        if options.load_nnc_metadata:
            raise UnsupportedFormatError("NNC metadata loading is not implemented")
        if options.lazy_geometry_arrays:
            raise UnsupportedFormatError("Lazy grid geometry arrays are not implemented")
        if options.validate_geometry_level is GeometryValidationLevel.FULL:
            raise UnsupportedFormatError(
                "Full corner-point geometry validation is not implemented"
            )
