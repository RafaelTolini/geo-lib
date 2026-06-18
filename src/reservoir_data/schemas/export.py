"""Export option schemas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.domain.units import UnitSystem


class ExportFormat(StrEnum):
    """Supported export container formats."""

    GRDECL = "grdecl"
    CSV = "csv"


class PropertyExportLayout(StrEnum):
    """Requested property array layout for export."""

    NATIVE = "native"
    ACTIVE = "active"
    GLOBAL = "global"


@dataclass(frozen=True, slots=True)
class GridTableExportOptions:
    """Options for exporting grid cell metadata as tabular rows."""

    include_geometry: bool = True
    include_simulator_indexes: bool = True


@dataclass(frozen=True, slots=True)
class PropertyExportOptions:
    """Options for exporting a grid property."""

    target_layout: PropertyExportLayout = PropertyExportLayout.NATIVE
    inactive_default: KeywordValue = None
    output_format: ExportFormat = ExportFormat.GRDECL
    include_cell_indexes: bool = False
    output_unit_system: UnitSystem | str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_layout",
            PropertyExportLayout(self.target_layout),
        )
        object.__setattr__(self, "output_format", ExportFormat(self.output_format))
        object.__setattr__(
            self,
            "output_unit_system",
            UnitSystem.optional(self.output_unit_system),
        )


@dataclass(frozen=True, slots=True)
class PropertyTableExportOptions:
    """Options for exporting grid property values as tabular rows."""

    target_layout: PropertyExportLayout = PropertyExportLayout.GLOBAL
    inactive_default: KeywordValue = None
    include_geometry: bool = True
    include_simulator_indexes: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_layout",
            PropertyExportLayout(self.target_layout),
        )
