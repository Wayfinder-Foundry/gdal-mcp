"""Filesystem-backed store for justification artifacts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.prompts.justification import Justification

__all__ = ["ReflectionStore", "DiskStore", "get_store"]


class ReflectionStore:
    """Abstract interface describing justification storage operations."""

    def get(self, key_path: str) -> dict[str, Any] | None:  # pragma: no cover - interface
        """Retrieve a justification by path."""
        raise NotImplementedError

    def put(
        self,
        key: str,
        value: Justification,
        domain: str,
    ) -> Path:  # pragma: no cover - interface
        """Store a justification and return its path."""
        raise NotImplementedError


class DiskStore(ReflectionStore):
    """Persist justifications to disk using operation-aware hashes."""

    def __init__(self, root: str = ".preflight/justifications") -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _risk_dir(self, domain: str) -> Path:
        prefix = domain.replace("_justification", "")
        path = self._root / prefix
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _path_for(self, key: str, domain: str) -> Path:
        return self._risk_dir(domain) / f"{key}.json"

    def path_for(self, key: str, domain: str) -> Path:
        """Return the filesystem path for a justification entry."""
        return self._path_for(key, domain)

    def has(self, key: str, domain: str) -> bool:
        """Return True if a justification exists for the given key/domain."""
        return self._path_for(key, domain).exists()

    def get(self, key_path: str) -> dict[str, Any] | None:
        """Retrieve a justification by path."""
        path = Path(key_path)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
        return None

    def put(self, key: str, value: Justification, domain: str) -> Path:
        """Atomically write justification to disk (temp + rename for crash safety)."""
        path = self._path_for(key, domain)
        payload = value.model_dump()
        payload["_meta"] = {"created_at": int(time.time())}

        # Write to temp file first, then atomic rename
        import tempfile

        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
        )
        try:
            with open(temp_fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(payload, indent=2))
            # Atomic rename (POSIX guarantees atomicity)
            Path(temp_path).rename(path)
        except Exception:
            # Clean up temp file on error
            Path(temp_path).unlink(missing_ok=True)
            raise

        return path


_DEFAULT_STORE: DiskStore | None = None


def get_store() -> DiskStore:
    """Return the shared disk-backed justification store instance."""
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = DiskStore()
    return _DEFAULT_STORE
