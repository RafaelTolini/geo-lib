"""Source file fingerprint value object."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from reservoir_data.exceptions.errors import FileReadError


@dataclass(frozen=True, slots=True)
class SourceFingerprint:
    """Identity fields used to invalidate cache/index entries."""

    path: str
    size: int
    mtime_ns: int
    sha256: str | None = None

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        include_checksum: bool = False,
    ) -> "SourceFingerprint":
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
            sha256=_sha256(source_path) if include_checksum else None,
        )

    def to_json(self) -> dict[str, int | str | None]:
        """Return a JSON-serializable representation."""

        return {
            "path": self.path,
            "size": self.size,
            "mtime_ns": self.mtime_ns,
            "sha256": self.sha256,
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
            sha256=(
                None
                if payload.get("sha256") is None
                else str(payload["sha256"])
            ),
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise FileReadError(f"Could not read source file {path}: {error}") from error
    return digest.hexdigest()
