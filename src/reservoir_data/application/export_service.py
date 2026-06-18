"""Application service for selective exports."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_record import KeywordRecord, KeywordValue
from reservoir_data.domain.property.grid_property import GridProperty, PropertyLayout
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.exceptions.errors import PropertyShapeError, UnsupportedFormatError
from reservoir_data.formats.grdecl.writer import GrdeclWriter
from reservoir_data.schemas.export import (
    GridTableExportOptions,
    PropertyExportLayout,
    PropertyExportOptions,
    PropertyTableExportOptions,
)

TableValue = KeywordValue | bool
TableRow = dict[str, TableValue]


@dataclass(frozen=True, slots=True)
class ExportService:
    """Coordinate supported export workflows."""

    grdecl_writer: GrdeclWriter = field(default_factory=GrdeclWriter)

    def grid_to_grdecl_text(
        self,
        grid: ReservoirGrid,
        include_actnum: bool = True,
    ) -> str:
        """Return a GRDECL geometry export for a supported grid."""

        return self.grdecl_writer.format_records(
            self._grid_records(grid, include_actnum=include_actnum)
        )

    def write_grid_grdecl(
        self,
        grid: ReservoirGrid,
        path: str | Path,
        include_actnum: bool = True,
    ) -> None:
        """Write a supported grid as GRDECL text."""

        Path(path).write_text(
            self.grid_to_grdecl_text(grid, include_actnum=include_actnum),
            encoding="utf-8",
        )

    def grid_cell_rows(
        self,
        grid: ReservoirGrid,
        options: GridTableExportOptions | None = None,
    ) -> tuple[TableRow, ...]:
        """Return one tabular row per global grid cell."""

        resolved_options = options or GridTableExportOptions()
        return tuple(
            self._cell_row(
                grid,
                global_index,
                include_geometry=resolved_options.include_geometry,
                include_simulator_indexes=resolved_options.include_simulator_indexes,
            )
            for global_index in range(grid.total_cell_count)
        )

    def write_grid_cell_csv(
        self,
        grid: ReservoirGrid,
        path: str | Path,
        options: GridTableExportOptions | None = None,
    ) -> None:
        """Write grid cell metadata as CSV rows."""

        self._write_csv(path, self.grid_cell_rows(grid, options=options))

    def grid_cell_dataframe(
        self,
        grid: ReservoirGrid,
        options: GridTableExportOptions | None = None,
    ) -> object:
        """Return grid cell metadata as a pandas DataFrame when installed."""

        return self._to_pandas(self.grid_cell_rows(grid, options=options))

    def property_to_grdecl_text(
        self,
        property_: GridProperty,
        options: PropertyExportOptions | None = None,
    ) -> str:
        """Return a GRDECL property export."""

        resolved_options = options or PropertyExportOptions()
        return self.grdecl_writer.format_record(
            property_.name,
            self._property_values(property_, resolved_options),
        )

    def write_property_grdecl(
        self,
        property_: GridProperty,
        path: str | Path,
        options: PropertyExportOptions | None = None,
    ) -> None:
        """Write a single supported property as GRDECL text."""

        Path(path).write_text(
            self.property_to_grdecl_text(property_, options=options),
            encoding="utf-8",
        )

    def property_rows(
        self,
        property_: GridProperty,
        options: PropertyTableExportOptions | None = None,
    ) -> tuple[TableRow, ...]:
        """Return tabular rows for a grid property."""

        grid = property_.grid
        if grid is None:
            raise PropertyShapeError(
                f"Property {property_.name} is not associated with a grid"
            )

        resolved_options = options or PropertyTableExportOptions()
        layout = self._table_layout(property_, resolved_options.target_layout)
        if layout is PropertyExportLayout.ACTIVE:
            values = property_.to_active_array()
            global_indexes = tuple(
                grid.active_cell_map.active_to_global_index(active_index)
                for active_index in range(grid.active_cell_count)
            )
        else:
            values = self._property_values(
                property_,
                PropertyExportOptions(
                    target_layout=PropertyExportLayout.GLOBAL,
                    inactive_default=resolved_options.inactive_default,
                ),
            )
            global_indexes = tuple(range(grid.total_cell_count))

        rows: list[TableRow] = []
        for value, global_index in zip(values, global_indexes, strict=True):
            row = self._cell_row(
                grid,
                global_index,
                include_geometry=resolved_options.include_geometry,
                include_simulator_indexes=resolved_options.include_simulator_indexes,
            )
            row["property"] = property_.name
            row["value"] = value
            rows.append(row)
        return tuple(rows)

    def write_property_csv(
        self,
        property_: GridProperty,
        path: str | Path,
        options: PropertyTableExportOptions | None = None,
    ) -> None:
        """Write one grid property as CSV rows."""

        self._write_csv(path, self.property_rows(property_, options=options))

    def property_dataframe(
        self,
        property_: GridProperty,
        options: PropertyTableExportOptions | None = None,
    ) -> object:
        """Return one property as a pandas DataFrame when installed."""

        return self._to_pandas(self.property_rows(property_, options=options))

    def properties_to_grdecl_text(
        self,
        properties: PropertyCollection,
        names: Iterable[str] | None = None,
        options: PropertyExportOptions | None = None,
    ) -> str:
        """Return selected properties as GRDECL keyword text."""

        selected_names = properties.names() if names is None else tuple(names)
        return "\n".join(
            self.property_to_grdecl_text(
                self._required_property(properties, name),
                options=options,
            ).rstrip()
            for name in selected_names
        ) + "\n"

    def write_properties_grdecl(
        self,
        properties: PropertyCollection,
        path: str | Path,
        names: Iterable[str] | None = None,
        options: PropertyExportOptions | None = None,
    ) -> None:
        """Write selected properties as GRDECL keyword text."""

        Path(path).write_text(
            self.properties_to_grdecl_text(
                properties,
                names=names,
                options=options,
            ),
            encoding="utf-8",
        )

    def properties_to_table_rows(
        self,
        properties: PropertyCollection,
        names: Iterable[str] | None = None,
        options: PropertyTableExportOptions | None = None,
    ) -> tuple[TableRow, ...]:
        """Return selected properties as long-form tabular rows."""

        selected_names = properties.names() if names is None else tuple(names)
        rows: list[TableRow] = []
        for name in selected_names:
            rows.extend(
                self.property_rows(
                    self._required_property(properties, name),
                    options=options,
                )
            )
        return tuple(rows)

    def write_properties_csv(
        self,
        properties: PropertyCollection,
        path: str | Path,
        names: Iterable[str] | None = None,
        options: PropertyTableExportOptions | None = None,
    ) -> None:
        """Write selected properties as long-form CSV rows."""

        self._write_csv(
            path,
            self.properties_to_table_rows(
                properties,
                names=names,
                options=options,
            ),
        )

    def properties_to_dataframe(
        self,
        properties: PropertyCollection,
        names: Iterable[str] | None = None,
        options: PropertyTableExportOptions | None = None,
    ) -> object:
        """Return selected properties as a pandas DataFrame when installed."""

        return self._to_pandas(
            self.properties_to_table_rows(
                properties,
                names=names,
                options=options,
            )
        )

    def _grid_records(
        self,
        grid: ReservoirGrid,
        include_actnum: bool,
    ) -> tuple[KeywordRecord, ...]:
        dimensions = grid.dimensions
        records = [
            KeywordRecord.from_values(
                "SPECGRID",
                (dimensions.nx, dimensions.ny, dimensions.nz, 1, False),
            ),
            KeywordRecord.from_values("COORD", grid.geometry.export_coord()),
            KeywordRecord.from_values("ZCORN", grid.geometry.export_zcorn()),
        ]
        if include_actnum:
            records.append(
                KeywordRecord.from_values(
                    "ACTNUM",
                    tuple(1 if active else 0 for active in grid.active_cell_map.activity_mask),
                )
            )
        return tuple(records)

    def _property_values(
        self,
        property_: GridProperty,
        options: PropertyExportOptions,
    ) -> tuple[KeywordValue, ...]:
        if options.target_layout is PropertyExportLayout.NATIVE:
            return property_.values
        if options.target_layout is PropertyExportLayout.ACTIVE:
            if property_.layout is PropertyLayout.ACTIVE:
                return property_.values
            return property_.to_active_array()
        if property_.layout is PropertyLayout.GLOBAL:
            return property_.values
        return property_.to_global_array(default_value=options.inactive_default)

    def _table_layout(
        self,
        property_: GridProperty,
        target_layout: PropertyExportLayout,
    ) -> PropertyExportLayout:
        if target_layout is PropertyExportLayout.NATIVE:
            if property_.layout is PropertyLayout.ACTIVE:
                return PropertyExportLayout.ACTIVE
            if property_.layout is PropertyLayout.GLOBAL:
                return PropertyExportLayout.GLOBAL
            raise PropertyShapeError(
                f"Property {property_.name} layout is unknown and cannot be exported"
            )
        return target_layout

    def _cell_row(
        self,
        grid: ReservoirGrid,
        global_index: int,
        include_geometry: bool,
        include_simulator_indexes: bool,
    ) -> TableRow:
        i, j, k = grid.ijk_from_global(global_index)
        active_index = grid.active_cell_map.global_to_active_index(global_index)
        row: TableRow = {
            "i": i,
            "j": j,
            "k": k,
            "global_index": global_index,
            "active_index": active_index,
            "is_active": active_index is not None,
        }
        if include_simulator_indexes:
            row.update(
                {
                    "simulator_i": i + 1,
                    "simulator_j": j + 1,
                    "simulator_k": k + 1,
                    "simulator_global_index": global_index + 1,
                    "simulator_active_index": (
                        None if active_index is None else active_index + 1
                    ),
                }
            )
        if include_geometry:
            row.update(
                {
                    "top": grid.geometry.cell_top(global_index),
                    "bottom": grid.geometry.cell_bottom(global_index),
                    "depth": grid.geometry.cell_depth(global_index),
                    "thickness": grid.geometry.cell_thickness(global_index),
                }
            )
        return row

    def _write_csv(self, path: str | Path, rows: tuple[TableRow, ...]) -> None:
        if not rows:
            Path(path).write_text("", encoding="utf-8")
            return
        with Path(path).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _to_pandas(self, rows: tuple[TableRow, ...]) -> object:
        try:
            import pandas as pd  # type: ignore[import-not-found]
        except ImportError as error:
            raise UnsupportedFormatError("pandas is not installed") from error
        return pd.DataFrame(list(rows))

    def _required_property(
        self,
        properties: PropertyCollection,
        name: str,
    ) -> GridProperty:
        property_ = properties.property(name)
        if property_ is None:
            raise ValueError(f"Property {name!r} was not found")
        return property_
