"""Application service for opening simulation cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Union

from reservoir_data.application.file_catalog import FileCatalog
from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.schemas.loading import LoadCaseOptions

if TYPE_CHECKING:
    from reservoir_data.domain.case.simulation_case import SimulationCase

CasePath = Union[str, Path]


@dataclass(slots=True)
class CaseLoader:
    """Orchestrates case discovery and facade construction."""

    catalog: FileCatalog = field(default_factory=FileCatalog)

    def load(
        self, path_or_basename: CasePath, options: LoadCaseOptions | None = None
    ) -> "SimulationCase":
        """Return a `SimulationCase` discovered from a path or basename."""

        from reservoir_data.domain.case.simulation_case import SimulationCase

        resolved_options = options or LoadCaseOptions()
        manifest = self.load_manifest(path_or_basename, resolved_options)
        return SimulationCase(
            case_name=manifest.case_name,
            root_path=manifest.root_path,
            manifest=manifest,
            options=resolved_options,
        )

    def load_manifest(
        self, path_or_basename: CasePath, options: LoadCaseOptions | None = None
    ) -> CaseManifest:
        """Discover and return the case manifest without parsing payloads."""

        return self.catalog.discover(path_or_basename, options or LoadCaseOptions())
