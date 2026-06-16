"""Keyword value type classification."""

from enum import StrEnum


class KeywordType(StrEnum):
    """Conservative type classification for keyword record elements."""

    INTEGER = "integer"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    LOGICAL = "logical"
    DEFAULTED = "defaulted"
    MIXED = "mixed"
