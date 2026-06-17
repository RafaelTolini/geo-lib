"""RFT/PLT dataset domain object."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reservoir_data.domain.rft.rft_record import RftRecord
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
