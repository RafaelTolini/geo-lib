"""Binary endian configuration."""

from enum import StrEnum


class Endianness(StrEnum):
    """Endian order used by binary record markers."""

    LITTLE = "little"
    BIG = "big"

    @property
    def struct_prefix(self) -> str:
        """Return the `struct` prefix for this endian order."""

        if self is Endianness.LITTLE:
            return "<"
        return ">"
