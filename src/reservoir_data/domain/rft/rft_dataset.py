"""RFT/PLT dataset domain object."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from reservoir_data.domain.rft.rft_record import RftRecord, _write_measurement_rows
from reservoir_data.exceptions.errors import RftDataError


@dataclass(frozen=True, slots=True)
class RftDataset:
    """Collection of RFT/PLT records for one case."""

    records: tuple[RftRecord, ...]
    sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "records",
            tuple(
                sorted(
                    self.records,
                    key=lambda record: (
                        record.report_date,
                        record.well_name,
                        record.record_type,
                    ),
                )
            ),
        )
        object.__setattr__(self, "sources", tuple(self.sources))

    def wells(self) -> tuple[str, ...]:
        """Return well names with RFT/PLT records."""

        return tuple(sorted({record.well_name for record in self.records}))

    def dates(self) -> tuple[date, ...]:
        """Return report dates with RFT/PLT records."""

        return tuple(sorted({record.report_date for record in self.records}))

    def record_types(self) -> tuple[str, ...]:
        """Return available RFT/PLT record types."""

        return tuple(sorted({record.record_type for record in self.records}))

    def records_for(
        self,
        well: str | None = None,
        report_date: date | None = None,
        record_type: str | None = None,
    ) -> tuple[RftRecord, ...]:
        """Return records matching optional well/date/type filters."""

        normalized_well = None if well is None else well.strip().upper()
        normalized_type = None if record_type is None else record_type.strip().upper()
        return tuple(
            record
            for record in self.records
            if (normalized_well is None or record.well_name == normalized_well)
            and (report_date is None or record.report_date == report_date)
            and (normalized_type is None or record.record_type == normalized_type)
        )

    def select(
        self,
        well: str | None = None,
        report_date: date | None = None,
        record_type: str | None = None,
    ) -> "RftDataset":
        """Return a dataset containing only matching RFT/PLT records."""

        return RftDataset(
            records=self.records_for(
                well=well,
                report_date=report_date,
                record_type=record_type,
            ),
            sources=self.sources,
        )

    def record(
        self,
        well: str,
        report_date: date,
        record_type: str | None = None,
    ) -> RftRecord:
        """Return a record by well, date, and optional type."""

        normalized_well = well.strip().upper()
        normalized_type = None if record_type is None else record_type.strip().upper()
        matches = tuple(
            record
            for record in self.records
            if record.well_name == normalized_well
            and record.report_date == report_date
            and (
                normalized_type is None
                or record.record_type == normalized_type
            )
        )
        if not matches:
            raise RftDataError(
                f"No RFT/PLT record exists for well {normalized_well!r} "
                f"on {report_date}"
            )
        if len(matches) > 1:
            raise RftDataError(
                f"Multiple RFT/PLT records exist for well {normalized_well!r} "
                f"on {report_date}; specify record_type"
            )
        return matches[0]

    def header_rows(self) -> tuple[dict[str, object], ...]:
        """Return one metadata row per RFT/PLT record."""

        return tuple(
            {
                "WELL": record.well_name,
                "DATE": record.report_date.isoformat(),
                "TYPE": record.record_type,
                "SOURCE": record.source,
                "MEASUREMENTS_LOADED": record.is_measurements_loaded,
            }
            for record in self.records
        )

    def to_csv(self, path: str | Path) -> None:
        """Write RFT/PLT record metadata to CSV."""

        rows = self.header_rows()
        fieldnames = [
            "WELL",
            "DATE",
            "TYPE",
            "SOURCE",
            "MEASUREMENTS_LOADED",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def measurement_rows(
        self,
        well: str | None = None,
        report_date: date | None = None,
        record_type: str | None = None,
    ) -> tuple[dict[str, object], ...]:
        """Return flattened measurement rows for matching records."""

        rows: list[dict[str, object]] = []
        for record in self.records_for(
            well=well,
            report_date=report_date,
            record_type=record_type,
        ):
            rows.extend(record.measurement_rows())
        return tuple(rows)

    def measurements_to_csv(
        self,
        path: str | Path,
        well: str | None = None,
        report_date: date | None = None,
        record_type: str | None = None,
    ) -> None:
        """Write flattened measurement rows for matching records to CSV."""

        _write_measurement_rows(
            path,
            self.measurement_rows(
                well=well,
                report_date=report_date,
                record_type=record_type,
            ),
        )
