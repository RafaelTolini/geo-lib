"""Loading option schemas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterable

from reservoir_data.domain.format.file_format import FileCategory


class FormattedFilePreference(StrEnum):
    """Preference used when multiple formatted states are available."""

    AUTO = "auto"
    FORMATTED = "formatted"
    UNFORMATTED = "unformatted"


class CachePolicy(StrEnum):
    """Cache/index behavior for future large-file workflows."""

    DISABLED = "disabled"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"


class GeometryValidationLevel(StrEnum):
    """Supported grid geometry validation depth."""

    NONE = "none"
    BASIC = "basic"
    FULL = "full"


class RestartGridAssociationMode(StrEnum):
    """How restart reports should be associated with a loaded grid."""

    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


class SummaryKeySeparatorPolicy(StrEnum):
    """Summary vector key separator policy."""

    COLON = "colon"


class SummaryTimeUnitPolicy(StrEnum):
    """Summary time-axis unit policy."""

    DAYS = "days"


@dataclass(frozen=True, slots=True)
class LoadCaseOptions:
    """Options for discovering and opening a simulation case."""

    root_path: Path | None = None
    strict_discovery: bool = True
    preferred_format: FormattedFilePreference = FormattedFilePreference.AUTO
    sniff_payload_format: bool = False
    file_categories: Iterable[FileCategory] | None = None
    lazy_loading: bool = True
    cache_policy: CachePolicy = CachePolicy.DISABLED

    def __post_init__(self) -> None:
        if self.root_path is not None:
            object.__setattr__(self, "root_path", Path(self.root_path).expanduser())
        object.__setattr__(
            self, "preferred_format", FormattedFilePreference(self.preferred_format)
        )
        object.__setattr__(self, "cache_policy", CachePolicy(self.cache_policy))
        if self.file_categories is not None:
            object.__setattr__(
                self,
                "file_categories",
                frozenset(FileCategory(category) for category in self.file_categories),
            )


@dataclass(frozen=True, slots=True)
class GridLoadOptions:
    """Options for loading supported grid geometry."""

    apply_coordinate_transforms: bool = False
    load_local_grids: bool = False
    load_nnc_metadata: bool = False
    validate_geometry_level: GeometryValidationLevel = GeometryValidationLevel.BASIC
    lazy_geometry_arrays: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "validate_geometry_level",
            GeometryValidationLevel(self.validate_geometry_level),
        )


@dataclass(frozen=True, slots=True)
class RestartLoadOptions:
    """Options for loading supported restart data."""

    requested_report_steps: Iterable[int] | None = None
    header_only: bool = False
    load_well_data: bool = False
    load_segment_data: bool = True
    grid_association_mode: RestartGridAssociationMode = RestartGridAssociationMode.NONE
    lazy_keyword_arrays: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "grid_association_mode",
            RestartGridAssociationMode(self.grid_association_mode),
        )
        if self.requested_report_steps is not None:
            object.__setattr__(
                self,
                "requested_report_steps",
                tuple(int(step) for step in self.requested_report_steps),
            )


@dataclass(frozen=True, slots=True)
class SummaryLoadOptions:
    """Options for loading supported summary data."""

    lazy_vectors: bool = True
    include_restart_metadata: bool = False
    key_separator_policy: SummaryKeySeparatorPolicy = SummaryKeySeparatorPolicy.COLON
    time_unit_policy: SummaryTimeUnitPolicy = SummaryTimeUnitPolicy.DAYS
    vector_filter: Iterable[str] | None = None
    strict_metadata_validation: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "key_separator_policy",
            SummaryKeySeparatorPolicy(self.key_separator_policy),
        )
        object.__setattr__(
            self,
            "time_unit_policy",
            SummaryTimeUnitPolicy(self.time_unit_policy),
        )
        if self.vector_filter is not None:
            object.__setattr__(
                self,
                "vector_filter",
                tuple(key.strip() for key in self.vector_filter if key.strip()),
            )
