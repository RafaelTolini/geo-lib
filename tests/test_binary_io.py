from io import BytesIO
import struct

import pytest

from reservoir_data.exceptions.errors import EncodingError, ParseError
from reservoir_data.infrastructure.binary_io.endianness import Endianness
from reservoir_data.infrastructure.binary_io.fortran_record_reader import (
    FortranRecordReader,
    detect_fortran_record_endianness,
)


def _record(
    payload: bytes,
    endianness: Endianness = Endianness.LITTLE,
    marker_byte_count: int = 4,
) -> bytes:
    code = "I" if marker_byte_count == 4 else "Q"
    marker = struct.pack(
        f"{endianness.struct_prefix}{code}",
        len(payload),
    )
    return marker + payload + marker


def test_fortran_record_reader_reads_valid_records() -> None:
    stream = BytesIO(_record(b"ABC") + _record(b"DEFG"))
    reader = FortranRecordReader(stream, endianness=Endianness.LITTLE)

    first = reader.read_record()
    second = reader.read_record()

    assert first is not None
    assert first.payload == b"ABC"
    assert first.record_length == 3
    assert first.offset == 0
    assert second is not None
    assert second.payload == b"DEFG"
    assert reader.read_record() is None


def test_fortran_record_reader_supports_big_endian_and_detection() -> None:
    stream = BytesIO(_record(b"BIG", Endianness.BIG))

    assert detect_fortran_record_endianness(stream) is Endianness.BIG
    assert stream.tell() == 0

    record = FortranRecordReader(stream, endianness=Endianness.BIG).read_record()

    assert record is not None
    assert record.payload == b"BIG"


def test_fortran_record_reader_detects_marker_mismatch() -> None:
    stream = BytesIO(struct.pack("<I", 3) + b"ABC" + struct.pack("<I", 4))

    with pytest.raises(ParseError, match="marker mismatch"):
        FortranRecordReader(stream).read_record()


def test_fortran_record_reader_detects_truncated_records() -> None:
    with pytest.raises(ParseError, match="Truncated record marker"):
        FortranRecordReader(BytesIO(b"\x03\x00")).read_record()

    with pytest.raises(ParseError, match="Truncated record payload"):
        FortranRecordReader(BytesIO(struct.pack("<I", 4) + b"AB")).read_record()

    with pytest.raises(ParseError, match="Truncated trailing record marker"):
        FortranRecordReader(
            BytesIO(struct.pack("<I", 3) + b"ABC" + b"\x03\x00")
        ).read_record()


def test_fortran_record_reader_rejects_implausible_text_as_unformatted() -> None:
    stream = BytesIO(b"PORO 1 /")

    with pytest.raises(ParseError, match="exceeds configured maximum"):
        FortranRecordReader(stream, max_record_length=1024).read_record()


def test_fortran_record_endianness_detection_reports_invalid_streams() -> None:
    with pytest.raises(EncodingError, match="Cannot detect"):
        detect_fortran_record_endianness(BytesIO(b"\x01\x02"))

    with pytest.raises(EncodingError, match="Could not detect"):
        detect_fortran_record_endianness(
            BytesIO(struct.pack("<I", 3) + b"ABC" + struct.pack("<I", 4))
        )
