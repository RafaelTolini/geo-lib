"""Minimal INIT/property reader."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from reservoir_data.domain.grid.reservoir_grid import ReservoirGrid
from reservoir_data.domain.keyword.keyword_dataset import KeywordDataset
from reservoir_data.domain.property.grid_property import GridProperty
from reservoir_data.domain.property.property_collection import PropertyCollection
from reservoir_data.exceptions.errors import FileReadError, MissingKeywordError, ParseError
from reservoir_data.formats.common.formatted_keyword_reader import FormattedKeywordReader
from reservoir_data.formats.grdecl.tokenizer import GrdeclToken, GrdeclTokenKind


TokenRecord = tuple[GrdeclToken, ...]


@dataclass(frozen=True, slots=True)
class InitReader:
    """Read minimal formatted INIT/property keyword files."""

    keyword_reader: FormattedKeywordReader = field(
        default_factory=FormattedKeywordReader
    )

    def read(
        self,
        path: str | Path,
        grid: ReservoirGrid | None = None,
        names: Sequence[str] | None = None,
        lazy: bool = False,
    ) -> PropertyCollection:
        """Read properties from a formatted INIT file."""

        if lazy:
            return self._read_lazy(path, grid=grid, names=names)
        dataset = self.keyword_reader.read(path)
        return self.from_dataset(dataset, grid=grid, names=names)

    def from_dataset(
        self,
        dataset: KeywordDataset,
        grid: ReservoirGrid | None = None,
        names: Sequence[str] | None = None,
    ) -> PropertyCollection:
        """Build a property collection from a parsed keyword dataset."""

        records = []
        if names is None:
            records = list(dataset.records)
        else:
            for name in names:
                record = dataset.record(name)
                if record is None:
                    raise MissingKeywordError(f"Property {name!r} was not found")
                records.append(record)

        properties = tuple(
            GridProperty.from_record(record, grid=grid) for record in records
        )
        return PropertyCollection(properties=properties, source=dataset.source)

    def _read_lazy(
        self,
        path: str | Path,
        grid: ReservoirGrid | None,
        names: Sequence[str] | None,
    ) -> PropertyCollection:
        source_path = Path(path)
        records = self._records_from_path(source_path)
        records_by_name = {record[0].text.strip().upper(): record for record in records}
        selected_names = (
            tuple(records_by_name)
            if names is None
            else tuple(name.strip().upper() for name in names)
        )
        missing = tuple(name for name in selected_names if name not in records_by_name)
        if missing:
            raise MissingKeywordError(f"Property {missing[0]!r} was not found")

        loaders = {
            name: self._property_loader(
                name=name,
                tokens=records_by_name[name],
                source=str(source_path),
                grid=grid,
            )
            for name in selected_names
        }
        return PropertyCollection(
            properties=(),
            property_loaders=loaders,
            source=str(source_path),
        )

    def _property_loader(
        self,
        name: str,
        tokens: TokenRecord,
        source: str,
        grid: ReservoirGrid | None,
    ):
        def load_property() -> GridProperty:
            dataset = self.keyword_reader.parser.parse_tokens(tokens, source=source)
            record = dataset.record(name)
            if record is None:
                raise MissingKeywordError(f"Property {name!r} was not found")
            return GridProperty.from_record(record, grid=grid)

        return load_property

    def _records_from_path(self, path: Path) -> tuple[TokenRecord, ...]:
        try:
            data = path.read_bytes()
        except OSError as error:
            raise FileReadError(f"Could not read INIT file {path}: {error}") from error
        if b"\x00" in data:
            raise ParseError(
                "Formatted INIT reader received binary-looking data; "
                "binary INIT decoding is not implemented"
            )
        try:
            text = data.decode(self.keyword_reader.encoding)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Could not decode formatted INIT data as "
                f"{self.keyword_reader.encoding}"
            ) from error
        return self._split_records(
            tuple(self.keyword_reader.parser.tokenizer.iter_tokens(text))
        )

    def _split_records(
        self,
        tokens: tuple[GrdeclToken, ...],
    ) -> tuple[TokenRecord, ...]:
        records: list[TokenRecord] = []
        current: list[GrdeclToken] = []
        for token in tokens:
            current.append(token)
            if token.kind is GrdeclTokenKind.TERMINATOR:
                records.append(tuple(current))
                current = []
        if current:
            raise ParseError(
                f"Unterminated INIT keyword record starting with {current[0].text!r}"
            )
        if not records:
            raise ParseError("INIT file contains no keyword records")
        return tuple(records)
