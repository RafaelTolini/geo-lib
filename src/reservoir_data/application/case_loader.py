"""Use case for opening a simulation case manifest."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.application.file_catalog import FileCatalog
from reservoir_data.domain.case.case_manifest import CaseManifest
from reservoir_data.schemas.loading import LoadCaseOptions


@dataclass(frozen=True, slots=True)
class CaseLoader:
    """Load the lightweight manifest for a simulation case."""

    file_catalog: FileCatalog = field(default_factory=FileCatalog)

    def load_manifest(
        self,
        path_or_basename: str | Path,
        options: LoadCaseOptions | None = None,
    ) -> CaseManifest:
        """Discover files and return a manifest without parsing payloads."""

        return self.file_catalog.discover(path_or_basename, options)
