"""User-facing simulation case object."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, Sequence, Union

from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.deck import DeckMetadata
from reservoir_data.domain.format.file_format import FileCategory
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.domain.restart.restart_dataset import RestartDataset
from reservoir_data.domain.rft.rft_dataset import RftDataset
from reservoir_data.domain.summary.summary_dataset import SummaryDataset
from reservoir_data.domain.well.well_dataset import WellDataset
from reservoir_data.exceptions.errors import FileReadError, UnsupportedFormatError
from reservoir_data.schemas.detection import FormatDetectionResult
from reservoir_data.schemas.export import (
    GridTableExportOptions,
    PropertyExportOptions,
    PropertyTableExportOptions,
)
from reservoir_data.schemas.loading import (
    GridLoadOptions,
    LoadCaseOptions,
    RestartGridAssociationMode,
    RestartLoadOptions,
    SummaryLoadOptions,
)

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

    def file_rows(self) -> tuple[dict[str, object], ...]:
        """Return discovered file rows without loading payloads."""

        return self.manifest.file_rows()

    def files_to_csv(self, path: CasePath) -> None:
        """Write discovered file rows to CSV."""

        self.manifest.files_to_csv(path)

    def load_deck_metadata(self) -> DeckMetadata:
        """Load externally useful metadata from a supported `.DATA` deck."""

        self._require_category(FileCategory.DECK, "deck")
        from reservoir_data.application.deck_service import DeckService

        return DeckService().load_metadata(
            self.manifest,
            preference=self.options.preferred_format,
        )

    def load_grid(self, options: GridLoadOptions | None = None) -> ReservoirGrid:
        self._require_category(FileCategory.GRID, "grid")
        from reservoir_data.application.grid_property_service import (
            GridPropertyService,
        )

        return GridPropertyService().load_grid(
            self.manifest,
            preference=self.options.preferred_format,
            options=options,
        )

    def load_properties(
        self, names: Sequence[str] | None = None
    ) -> PropertyCollection:
        self._require_category(FileCategory.INIT, "initialization/property")
        from reservoir_data.application.grid_property_service import (
            GridPropertyService,
        )

        service = GridPropertyService()
        grid = None
        if self.has_data(FileCategory.GRID):
            grid = service.load_grid(
                self.manifest,
                preference=self.options.preferred_format,
            )
        return service.load_properties(
            self.manifest,
            names=names,
            grid=grid,
            preference=self.options.preferred_format,
            lazy=self.options.lazy_loading,
        )

    def load_restarts(
        self,
        associate_grid: bool = False,
        options: RestartLoadOptions | None = None,
    ) -> RestartDataset:
        self._require_category(FileCategory.RESTART, "restart")
        from reservoir_data.application.grid_property_service import (
            GridPropertyService,
        )
        from reservoir_data.application.restart_service import RestartService

        resolved_options = options or RestartLoadOptions()
        grid_association = resolved_options.grid_association_mode
        grid = None
        should_associate_grid = (
            associate_grid
            or grid_association is RestartGridAssociationMode.OPTIONAL
            or grid_association is RestartGridAssociationMode.REQUIRED
        )
        if should_associate_grid and self.has_data(FileCategory.GRID):
            grid = GridPropertyService().load_grid(
                self.manifest,
                preference=self.options.preferred_format,
            )
        elif grid_association is RestartGridAssociationMode.REQUIRED:
            raise FileReadError(
                f"No grid files were discovered for case '{self.case_name}'"
            )
        return RestartService().load_restarts(
            self.manifest,
            grid=grid,
            preference=self.options.preferred_format,
            options=resolved_options,
        )

    def load_summary(self, options: SummaryLoadOptions | None = None) -> SummaryDataset:
        if not (
            self.has_data(FileCategory.SUMMARY_METADATA)
            or self.has_data(FileCategory.SUMMARY_DATA)
        ):
            raise FileReadError(
                f"No summary files were discovered for case '{self.case_name}'"
            )
        from reservoir_data.application.summary_service import SummaryService

        return SummaryService().load_summary(
            self.manifest,
            preference=self.options.preferred_format,
            cache_policy=self.options.cache_policy,
            options=options,
        )

    def load_wells(self, load_segments: bool = True) -> WellDataset:
        self._require_category(FileCategory.RESTART, "restart well")
        from reservoir_data.application.grid_property_service import (
            GridPropertyService,
        )
        from reservoir_data.application.well_service import WellService

        grid = None
        if self.has_data(FileCategory.GRID):
            grid = GridPropertyService().load_grid(
                self.manifest,
                preference=self.options.preferred_format,
            )
        return WellService().load_wells(
            self.manifest,
            load_segments=load_segments,
            grid=grid,
            preference=self.options.preferred_format,
        )

    def load_rft(self) -> RftDataset:
        if not (self.has_data(FileCategory.RFT) or self.has_data(FileCategory.PLT)):
            raise FileReadError(
                f"No RFT/PLT files were discovered for case '{self.case_name}'"
            )
        from reservoir_data.application.grid_property_service import (
            GridPropertyService,
        )
        from reservoir_data.application.rft_service import RftService

        grid = None
        if self.has_data(FileCategory.GRID):
            grid = GridPropertyService().load_grid(
                self.manifest,
                preference=self.options.preferred_format,
            )
        return RftService().load_rft(
            self.manifest,
            grid=grid,
            preference=self.options.preferred_format,
        )

    def export_grid_grdecl(self, path: CasePath) -> None:
        """Export the supported grid geometry as GRDECL text."""

        from reservoir_data.application.export_service import ExportService

        ExportService().write_grid_grdecl(self.load_grid(), path)

    def export_grid_cell_csv(
        self,
        path: CasePath,
        options: GridTableExportOptions | None = None,
    ) -> None:
        """Export grid cell metadata as CSV rows."""

        from reservoir_data.application.export_service import ExportService

        ExportService().write_grid_cell_csv(self.load_grid(), path, options=options)

    def grid_cell_dataframe(
        self,
        options: GridTableExportOptions | None = None,
    ) -> object:
        """Return grid cell metadata as a pandas DataFrame when installed."""

        from reservoir_data.application.export_service import ExportService

        return ExportService().grid_cell_dataframe(self.load_grid(), options=options)

    def export_properties_grdecl(
        self,
        path: CasePath,
        names: Sequence[str] | None = None,
        options: PropertyExportOptions | None = None,
    ) -> None:
        """Export selected supported properties as GRDECL text."""

        from reservoir_data.application.export_service import ExportService

        ExportService().write_properties_grdecl(
            self.load_properties(names=names),
            path,
            names=names,
            options=options,
        )

    def export_properties_csv(
        self,
        path: CasePath,
        names: Sequence[str] | None = None,
        options: PropertyTableExportOptions | None = None,
    ) -> None:
        """Export selected supported properties as long-form CSV rows."""

        from reservoir_data.application.export_service import ExportService

        ExportService().write_properties_csv(
            self.load_properties(names=names),
            path,
            names=names,
            options=options,
        )

    def properties_dataframe(
        self,
        names: Sequence[str] | None = None,
        options: PropertyTableExportOptions | None = None,
    ) -> object:
        """Return selected property rows as a pandas DataFrame when installed."""

        from reservoir_data.application.export_service import ExportService

        return ExportService().properties_to_dataframe(
            self.load_properties(names=names),
            names=names,
            options=options,
        )

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
