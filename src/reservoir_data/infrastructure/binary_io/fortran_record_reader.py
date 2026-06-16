"""Fortran-style binary record reader."""

from __future__ import annotations

import struct
from collections.abc import Iterator
from dataclasses import dataclass
from typing import BinaryIO

from reservoir_data.exceptions.errors import EncodingError, ParseError
from reservoir_data.infrastructure.binary_io.endianness import Endianness
from reservoir_data.infrastructure.binary_io.fortran_record import FortranRecord


@dataclass(frozen=True, slots=True)
class FortranRecordReader:
    """Read unformatted Fortran records from a binary stream."""

    stream: BinaryIO
    endianness: Endianness = Endianness.LITTLE
    marker_byte_count: int = 4
    max_record_length: int = 512 * 1024 * 1024

    def __post_init__(self) -> None:
        object.__setattr__(self, "endianness", Endianness(self.endianness))
        if self.marker_byte_count not in {4, 8}:
            raise ValueError("marker_byte_count must be 4 or 8")
        if self.max_record_length <= 0:
            raise ValueError("max_record_length must be positive")

    def read_record(self) -> FortranRecord | None:
        """Read the next record, returning `None` at clean EOF."""

        offset = self.stream.tell()
        header = self.stream.read(self.marker_byte_count)
        if header == b"":
            return None
        if len(header) != self.marker_byte_count:
            raise ParseError(
                f"Truncated record marker at offset {offset}: got {len(header)} "
                f"of {self.marker_byte_count} bytes"
            )

        record_length = self._decode_marker(header)
        if record_length > self.max_record_length:
            raise ParseError(
                f"Record length {record_length} at offset {offset} exceeds "
                f"configured maximum {self.max_record_length}"
            )

        payload = self.stream.read(record_length)
        if len(payload) != record_length:
            raise ParseError(
                f"Truncated record payload at offset {offset}: expected "
                f"{record_length} bytes, got {len(payload)}"
            )

        footer = self.stream.read(self.marker_byte_count)
        if len(footer) != self.marker_byte_count:
            raise ParseError(
                f"Truncated trailing record marker at offset {offset}: got "
                f"{len(footer)} of {self.marker_byte_count} bytes"
            )

        trailing_length = self._decode_marker(footer)
        if trailing_length != record_length:
            raise ParseError(
                f"Record marker mismatch at offset {offset}: leading marker "
                f"{record_length}, trailing marker {trailing_length}"
            )

        return FortranRecord(
            payload=payload,
            offset=offset,
            marker_byte_count=self.marker_byte_count,
        )

    def iter_records(self) -> Iterator[FortranRecord]:
        """Yield records until clean EOF."""

        while True:
            record = self.read_record()
            if record is None:
                break
            yield record

    def _decode_marker(self, marker: bytes) -> int:
        code = "I" if self.marker_byte_count == 4 else "Q"
        return int(struct.unpack(f"{self.endianness.struct_prefix}{code}", marker)[0])


def detect_fortran_record_endianness(
    stream: BinaryIO,
    marker_byte_count: int = 4,
    max_record_length: int = 512 * 1024 * 1024,
) -> Endianness:
    """Detect endian order by checking the first record's matching markers."""

    if marker_byte_count not in {4, 8}:
        raise ValueError("marker_byte_count must be 4 or 8")
    if max_record_length <= 0:
        raise ValueError("max_record_length must be positive")

    start = stream.tell()
    try:
        marker = stream.read(marker_byte_count)
        if len(marker) != marker_byte_count:
            raise EncodingError(
                f"Cannot detect endian order from {len(marker)} marker bytes"
            )

        matches: list[Endianness] = []
        for endianness in Endianness:
            length = _decode_marker(marker, endianness, marker_byte_count)
            if length > max_record_length:
                continue

            stream.seek(start + marker_byte_count + length)
            trailing_marker = stream.read(marker_byte_count)
            if len(trailing_marker) != marker_byte_count:
                continue
            trailing_length = _decode_marker(
                trailing_marker, endianness, marker_byte_count
            )
            if trailing_length == length:
                matches.append(endianness)

        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise EncodingError("Could not detect Fortran record endian order")
        raise EncodingError("Fortran record endian detection was ambiguous")
    finally:
        stream.seek(start)


def _decode_marker(
    marker: bytes, endianness: Endianness, marker_byte_count: int
) -> int:
    code = "I" if marker_byte_count == 4 else "Q"
    return int(struct.unpack(f"{endianness.struct_prefix}{code}", marker)[0])
