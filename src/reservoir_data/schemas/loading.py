"""Loading option value objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from reservoir_data.domain.format.file_format import FileCategory


class FormatPreference(str, Enum):
    """Preferred file encoding when multiple candidates exist."""

    AUTO = "auto"
    FORMATTED = "formatted"
    UNFORMATTED = "unformatted"


class CachePolicy(str, Enum):
    """Cache behavior for workflows that later support indexes."""

    DISABLED = "disabled"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"


@dataclass(frozen=True, slots=True)
class LoadCaseOptions:
    """Options used while discovering a simulation case."""

    root_path: Path | None = None
    strict_discovery: bool = False
    preferred_format: FormatPreference = FormatPreference.AUTO
    file_category_filters: frozenset[FileCategory] | None = None
    lazy_loading_default: bool = True
    cache_policy: CachePolicy = CachePolicy.DISABLED

    def __post_init__(self) -> None:
        if self.root_path is not None:
            object.__setattr__(self, "root_path", Path(self.root_path))
        object.__setattr__(
            self,
            "preferred_format",
            FormatPreference(self.preferred_format),
        )
        object.__setattr__(self, "cache_policy", CachePolicy(self.cache_policy))
        if self.file_category_filters is not None:
            object.__setattr__(
                self,
                "file_category_filters",
                frozenset(FileCategory(category) for category in self.file_category_filters),
            )

    @classmethod
    def with_category_filters(
        cls,
        categories: Iterable[FileCategory | str],
        *,
        root_path: str | Path | None = None,
        strict_discovery: bool = False,
        preferred_format: FormatPreference | str = FormatPreference.AUTO,
        lazy_loading_default: bool = True,
        cache_policy: CachePolicy | str = CachePolicy.DISABLED,
    ) -> "LoadCaseOptions":
        """Create options with normalized category filters."""

        return cls(
            root_path=Path(root_path) if root_path is not None else None,
            strict_discovery=strict_discovery,
            preferred_format=FormatPreference(preferred_format),
            file_category_filters=frozenset(FileCategory(category) for category in categories),
            lazy_loading_default=lazy_loading_default,
            cache_policy=CachePolicy(cache_policy),
        )

    def allows_category(self, category: FileCategory) -> bool:
        """Return whether discovery should keep this file category."""

        if self.file_category_filters is None:
            return True
        return category in self.file_category_filters
