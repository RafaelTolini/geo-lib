"""Explicit exception model for reservoir_data."""


class ReservoirDataError(Exception):
    """Base exception for all reservoir_data errors."""


class FileDetectionError(ReservoirDataError):
    """Raised when a case or file type cannot be identified safely."""


class FileReadError(ReservoirDataError):
    """Raised for missing, unreadable, or inaccessible files."""


class UnsupportedFormatError(ReservoirDataError):
    """Raised for recognized but unsupported file variants or workflows."""


class ParseError(ReservoirDataError):
    """Raised by format readers for malformed records or unexpected EOF."""


class EncodingError(ParseError):
    """Raised for binary encoding, endian, or header detection failures."""


class MissingKeywordError(ReservoirDataError):
    """Raised when a required keyword is absent."""


class InvalidReportStepError(ReservoirDataError):
    """Raised for unavailable report steps or invalid time queries."""


class InvalidCellIndexError(ReservoirDataError):
    """Raised for ambiguous or out-of-bounds cell indexes."""


class GridGeometryError(ReservoirDataError):
    """Raised for invalid or inconsistent grid geometry."""


class PropertyShapeError(ReservoirDataError):
    """Raised for active/global/grid-size mismatches."""


class SummaryDataError(ReservoirDataError):
    """Raised for inconsistent summary metadata or vector data."""


class WellDataError(ReservoirDataError):
    """Raised for missing or inconsistent well data."""


class RftDataError(ReservoirDataError):
    """Raised for missing or malformed RFT/PLT records."""
