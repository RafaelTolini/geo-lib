"""Binary I/O infrastructure for format readers."""

from reservoir_data.infrastructure.binary_io.endianness import Endianness
from reservoir_data.infrastructure.binary_io.fortran_record import FortranRecord
from reservoir_data.infrastructure.binary_io.fortran_record_reader import (
    FortranRecordReader,
    detect_fortran_record_endianness,
)

__all__ = [
    "Endianness",
    "FortranRecord",
    "FortranRecordReader",
    "detect_fortran_record_endianness",
]
