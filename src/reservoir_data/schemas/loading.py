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


@dataclass(frozen=True, slots=True)
class LoadCaseOptions:
    """Options for discovering and opening a simulation case."""

    root_path: Path | None = None
    strict_discovery: bool = True
    preferred_format: FormattedFilePreference = FormattedFilePreference.AUTO
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
