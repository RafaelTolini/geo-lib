"""Source file fingerprint value object."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reservoir_data.exceptions.errors import FileReadError


@dataclass(frozen=True, slots=True)
class SourceFingerprint:
    """Identity fields used to invalidate cache/index entries."""

    path: str
    size: int
    mtime_ns: int

    @classmethod
    def from_path(cls, path: str | Path) -> "SourceFingerprint":
        """Create a fingerprint from a source path."""

        source_path = Path(path)
        try:
            stat = source_path.stat()
        except OSError as error:
            raise FileReadError(f"Could not stat source file {source_path}: {error}") from error
        return cls(
            path=str(source_path.resolve()),
            size=stat.st_size,
            mtime_ns=stat.st_mtime_ns,
        )

    def to_json(self) -> dict[str, int | str]:
        """Return a JSON-serializable representation."""

        return {
            "path": self.path,
            "size": self.size,
            "mtime_ns": self.mtime_ns,
        }

    @classmethod
    def from_json(cls, payload: object) -> "SourceFingerprint":
        """Create a fingerprint from a decoded JSON object."""

        if not isinstance(payload, dict):
            raise ValueError("Source fingerprint payload must be an object")
        return cls(
            path=str(payload["path"]),
            size=int(payload["size"]),
            mtime_ns=int(payload["mtime_ns"]),
        )
