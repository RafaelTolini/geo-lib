"""Well dataset domain object."""

from __future__ import annotations

from dataclasses import dataclass

from reservoir_data.domain.well.well_timeline import WellTimeline
from reservoir_data.exceptions.errors import WellDataError


@dataclass(frozen=True, slots=True)
class WellDataset:
    """Collection of well timelines for one case."""

    timelines: tuple[WellTimeline, ...]
    sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        timelines = tuple(sorted(self.timelines, key=lambda item: item.well_name))
        names = [timeline.well_name for timeline in timelines]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise WellDataError(f"Duplicate well timelines: {duplicate_list}")
        object.__setattr__(self, "timelines", timelines)
        object.__setattr__(self, "sources", tuple(self.sources))

    def names(self) -> tuple[str, ...]:
        """Return well names."""

        return tuple(timeline.well_name for timeline in self.timelines)

    def timeline(self, well_name: str) -> WellTimeline:
        """Return one well timeline."""

        normalized = well_name.strip().upper()
        for timeline in self.timelines:
            if timeline.well_name == normalized:
                return timeline
        raise WellDataError(f"Well {normalized!r} was not found")
