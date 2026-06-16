"""Build grid domain objects from parsed GRDECL keywords."""

from __future__ import annotations

from dataclasses import dataclass, field

from reservoir_data.domain.grid.active_cell_map import ActiveCellMap
from reservoir_data.domain.grid.grid_dimensions import GridDimensions
from reservoir_data.domain.grid.grid_geometry import GridGeometry
from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.keyword.keyword_record import KeywordValue
from reservoir_data.exceptions.errors import GridGeometryError, MissingKeywordError
from reservoir_data.formats.grdecl.parser import GrdeclParser


@dataclass(frozen=True, slots=True)
class GrdeclGridBuilder:
    """Construct a minimal structured grid from GRDECL geometry keywords."""

    parser: GrdeclParser = field(default_factory=GrdeclParser)

    def build(self, dataset: KeywordDataset) -> ReservoirGrid:
        """Build a grid from `SPECGRID`, `COORD`, `ZCORN`, and optional `ACTNUM`."""

        specgrid = self._required_values(dataset, "SPECGRID")
        dimensions = self._dimensions_from_specgrid(specgrid)

        coord = self._numeric_values(dataset, "COORD")
        zcorn = self._numeric_values(dataset, "ZCORN")
        map_axes = None
        if dataset.has_keyword("MAPAXES"):
            map_axes = self._numeric_values(dataset, "MAPAXES")

        geometry = GridGeometry.from_sequences(
            dimensions=dimensions,
            coord=coord,
            zcorn=zcorn,
            map_axes=map_axes,
        )

        if dataset.has_keyword("ACTNUM"):
            active_map = ActiveCellMap.from_activity_values(
                self._activity_values(dataset), dimensions.total_cells
            )
        else:
            active_map = ActiveCellMap.all_active(dimensions.total_cells)

        return ReservoirGrid(
            dimensions=dimensions,
            geometry=geometry,
            active_cell_map=active_map,
        )

    def build_from_text(self, text: str, source: str | None = None) -> ReservoirGrid:
        """Parse GRDECL text and build a grid."""

        return self.build(self.parser.parse_text(text, source=source))

    def _required_values(
        self, dataset: KeywordDataset, keyword_name: str
    ) -> tuple[KeywordValue, ...]:
        try:
            record = dataset.record(keyword_name)
        except MissingKeywordError as error:
            raise GridGeometryError(f"Missing required grid keyword {keyword_name}") from error
        if record is None:
            raise GridGeometryError(f"Missing required grid keyword {keyword_name}")
        return record.values

    def _dimensions_from_specgrid(
        self, values: tuple[KeywordValue, ...]
    ) -> GridDimensions:
        if len(values) < 3:
            raise GridGeometryError("SPECGRID must contain at least nx, ny, and nz")
        nx = self._required_integer("SPECGRID", values[0])
        ny = self._required_integer("SPECGRID", values[1])
        nz = self._required_integer("SPECGRID", values[2])
        try:
            return GridDimensions(nx=nx, ny=ny, nz=nz)
        except ValueError as error:
            raise GridGeometryError(f"Invalid SPECGRID dimensions: {error}") from error

    def _numeric_values(
        self, dataset: KeywordDataset, keyword_name: str
    ) -> tuple[float, ...]:
        values = self._required_values(dataset, keyword_name)
        return tuple(self._required_number(keyword_name, value) for value in values)

    def _activity_values(self, dataset: KeywordDataset) -> tuple[int, ...]:
        values = self._required_values(dataset, "ACTNUM")
        return tuple(self._required_integer("ACTNUM", value) for value in values)

    def _required_integer(self, keyword_name: str, value: KeywordValue) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise GridGeometryError(
                f"{keyword_name} expected integer value, got {value!r}"
            )
        return value

    def _required_number(self, keyword_name: str, value: KeywordValue) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise GridGeometryError(
                f"{keyword_name} expected numeric value, got {value!r}"
            )
        return float(value)
