"""Explicit exception model for reservoir data workflows."""


class ReservoirDataError(Exception):
    """Base class for all package-specific errors."""


class FileDetectionError(ReservoirDataError):
    """Raised when a case or file type cannot be identified unambiguously."""


class FileReadError(ReservoirDataError):
    """Raised when a file or directory cannot be accessed."""


class UnsupportedFormatError(ReservoirDataError):
    """Raised for recognized workflows or variants that are not supported."""


class ParseError(ReservoirDataError):
    """Raised when a format reader encounters malformed content."""


class EncodingError(ParseError):
    """Raised for endian, encoding, or binary header detection failures."""


class MissingKeywordError(ReservoirDataError):
    """Raised when a required keyword is absent."""


class InvalidReportStepError(ReservoirDataError):
    """Raised for unavailable report steps or invalid time queries."""


class InvalidCellIndexError(ReservoirDataError):
    """Raised for ambiguous or out-of-bounds cell indexes."""


class GridGeometryError(ReservoirDataError):
    """Raised for invalid or inconsistent grid geometry."""


class PropertyShapeError(ReservoirDataError):
    """Raised for active/global/grid-size property shape mismatches."""


class SummaryDataError(ReservoirDataError):
    """Raised for inconsistent or malformed summary metadata or vector data."""


class WellDataError(ReservoirDataError):
    """Raised for missing or inconsistent well data."""


class RftDataError(ReservoirDataError):
    """Raised for missing or malformed RFT/PLT records."""
