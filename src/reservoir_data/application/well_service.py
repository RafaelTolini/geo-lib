"""Application service for well workflows."""

from __future__ import annotations

from dataclasses import dataclass, field

from reservoir_data.application.restart_service import RestartService
from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.well.well_dataset import WellDataset
from reservoir_data.formats.well.formatted_well_reader import FormattedWellReader
from reservoir_data.schemas.loading import FormattedFilePreference


@dataclass(frozen=True, slots=True)
class WellService:
    """Coordinate well timeline extraction from restart data."""

    restart_service: RestartService = field(default_factory=RestartService)
    well_reader: FormattedWellReader = field(default_factory=FormattedWellReader)

    def load_wells(
        self,
        manifest: CaseManifest,
        load_segments: bool = True,
        grid: ReservoirGrid | None = None,
        preference: FormattedFilePreference = FormattedFilePreference.AUTO,
    ) -> WellDataset:
        """Load supported well timelines from formatted restart records."""

        restarts = self.restart_service.load_restarts(
            manifest,
            grid=grid,
            preference=preference,
        )
        return self.well_reader.read(
            restarts,
            load_segments=load_segments,
            grid=grid,
        )
