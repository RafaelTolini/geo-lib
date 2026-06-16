"""Typed grid cell address."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CellIndexKind(StrEnum):
    """Addressing mode used by a `CellIndex`."""

    IJK = "ijk"
    GLOBAL = "global"
    ACTIVE = "active"


@dataclass(frozen=True, slots=True)
class CellIndex:
    """Explicit cell address, normalized to zero-based Python indexing."""

    i: int | None = None
    j: int | None = None
    k: int | None = None
    global_index: int | None = None
    active_index: int | None = None
    simulator_one_based: bool = False

    def __post_init__(self) -> None:
        has_ijk = self.i is not None or self.j is not None or self.k is not None
        if has_ijk and None in (self.i, self.j, self.k):
            raise ValueError("i, j, and k must be provided together")

        mode_count = sum(
            (
                has_ijk,
                self.global_index is not None,
                self.active_index is not None,
            )
        )
        if mode_count != 1:
            raise ValueError("CellIndex must use exactly one addressing mode")

        for name, value in (
            ("i", self.i),
            ("j", self.j),
            ("k", self.k),
            ("global_index", self.global_index),
            ("active_index", self.active_index),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative")

    @classmethod
    def ijk(
        cls, i: int, j: int, k: int, simulator_one_based: bool = False
    ) -> "CellIndex":
        """Create an IJK cell address."""

        if simulator_one_based:
            cls._validate_one_based("i", i)
            cls._validate_one_based("j", j)
            cls._validate_one_based("k", k)
            return cls(
                i=i - 1,
                j=j - 1,
                k=k - 1,
                simulator_one_based=True,
            )
        return cls(i=i, j=j, k=k)

    @classmethod
    def global_cell(
        cls, global_index: int, simulator_one_based: bool = False
    ) -> "CellIndex":
        """Create a global-index cell address."""

        if simulator_one_based:
            cls._validate_one_based("global_index", global_index)
            return cls(global_index=global_index - 1, simulator_one_based=True)
        return cls(global_index=global_index)

    @classmethod
    def active_cell(
        cls, active_index: int, simulator_one_based: bool = False
    ) -> "CellIndex":
        """Create an active-index cell address."""

        if simulator_one_based:
            cls._validate_one_based("active_index", active_index)
            return cls(active_index=active_index - 1, simulator_one_based=True)
        return cls(active_index=active_index)

    @property
    def kind(self) -> CellIndexKind:
        """Return the addressing mode."""

        if self.global_index is not None:
            return CellIndexKind.GLOBAL
        if self.active_index is not None:
            return CellIndexKind.ACTIVE
        return CellIndexKind.IJK

    def zero_based_ijk(self) -> tuple[int, int, int]:
        """Return zero-based IJK values for IJK-mode indexes."""

        if self.kind is not CellIndexKind.IJK:
            raise ValueError("CellIndex is not in IJK mode")
        if self.i is None or self.j is None or self.k is None:
            raise ValueError("Incomplete IJK address")
        return self.i, self.j, self.k

    def simulator_ijk(self) -> tuple[int, int, int]:
        """Return one-based simulator IJK values for IJK-mode indexes."""

        i, j, k = self.zero_based_ijk()
        return i + 1, j + 1, k + 1

    def simulator_global_index(self) -> int:
        """Return one-based simulator global index for global-mode indexes."""

        if self.global_index is None:
            raise ValueError("CellIndex is not in global-index mode")
        return self.global_index + 1

    def simulator_active_index(self) -> int:
        """Return one-based simulator active index for active-mode indexes."""

        if self.active_index is None:
            raise ValueError("CellIndex is not in active-index mode")
        return self.active_index + 1

    @staticmethod
    def _validate_one_based(name: str, value: int) -> None:
        if value <= 0:
            raise ValueError(f"{name} must be positive when simulator_one_based=True")
