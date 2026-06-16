"""Fortran-style binary record container."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FortranRecord:
    """One length-prefixed Fortran-style unformatted record."""

    payload: bytes
    offset: int
    marker_byte_count: int

    @property
    def record_length(self) -> int:
        """Length encoded in the record markers."""

        return len(self.payload)
