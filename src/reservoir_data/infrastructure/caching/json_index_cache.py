"""JSON index cache infrastructure."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from reservoir_data.infrastructure.caching.source_fingerprint import SourceFingerprint


@dataclass(slots=True)
class JsonIndexCache:
    """Optional JSON cache for reader indexes.

    Cache correctness never depends on this object. Entries are considered valid
    only when every source fingerprint exactly matches resolved path, size, and
    modification time.
    """

    cache_dir: Path
    writable: bool = False
    hits: int = 0
    misses: int = 0
    writes: int = 0
    checksum_sources: bool = False
    _version: int = field(default=1, init=False)

    def __post_init__(self) -> None:
        self.cache_dir = Path(self.cache_dir)

    def load(
        self,
        namespace: str,
        key: str,
        sources: Iterable[str | Path],
    ) -> dict[str, object] | None:
        """Load a cache payload if source fingerprints still match."""

        cache_path = self._path(namespace, key)
        expected = self._fingerprints(sources)
        try:
            with cache_path.open("r", encoding="utf-8") as stream:
                envelope = json.load(stream)
        except (OSError, json.JSONDecodeError):
            self.misses += 1
            return None

        if envelope.get("version") != self._version:
            self.misses += 1
            return None
        cached_sources = envelope.get("sources")
        try:
            actual = tuple(
                SourceFingerprint.from_json(item) for item in cached_sources
            )
        except (TypeError, ValueError, KeyError):
            self.misses += 1
            return None
        if actual != expected:
            self.misses += 1
            return None

        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            self.misses += 1
            return None
        self.hits += 1
        return payload

    def save(
        self,
        namespace: str,
        key: str,
        sources: Iterable[str | Path],
        payload: dict[str, object],
    ) -> None:
        """Write a cache payload when the cache is writable."""

        if not self.writable:
            return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self._path(namespace, key)
        envelope = {
            "version": self._version,
            "sources": [item.to_json() for item in self._fingerprints(sources)],
            "payload": payload,
        }
        with cache_path.open("w", encoding="utf-8") as stream:
            json.dump(envelope, stream, sort_keys=True)
        self.writes += 1

    def _path(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(f"{namespace}:{key}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _fingerprints(
        self,
        sources: Iterable[str | Path],
    ) -> tuple[SourceFingerprint, ...]:
        return tuple(
            SourceFingerprint.from_path(
                source,
                include_checksum=self.checksum_sources,
            )
            for source in sources
        )
