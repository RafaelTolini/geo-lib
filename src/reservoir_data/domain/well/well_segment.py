"""Well segment domain object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WellSegment:
    """One optional multi-segment well segment."""

    segment_id: int
    parent_id: int | None = None
    depth: float | None = None
    length: float | None = None

    def __post_init__(self) -> None:
        if self.segment_id <= 0:
            raise ValueError("segment_id must be positive")
        if self.parent_id is not None and self.parent_id <= 0:
            raise ValueError("parent_id must be positive when provided")
        if self.length is not None and self.length < 0:
            raise ValueError("length must be non-negative")
