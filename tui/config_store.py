"""Merged JSON configuration with explicit write ownership."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


# Keys owned by each file. Extend this map only when ownership is confirmed
# against the project's existing configuration schema.
OWNER: dict[str, str] = {
    "master": "config.json",
    "captive": "captive.json",
}


class ConfigStore:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or os.environ.get("APMANAGER_CONFIG_DIR", ".")).resolve()
        self._sources: dict[str, dict[str, Any]] = {}
        self._merged: dict[str, Any] = {}
        self.reload()

    @property
    def data(self) -> dict[str, Any]:
        return self._merged.copy()

    def _read(self, filename: str) -> dict[str, Any]:
        path = self.root / filename
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise ValueError(f"Configuration root must be an object: {path}")
        return value

    def reload(self) -> dict[str, Any]:
        self._sources = {name: self._read(filename) for name, filename in OWNER.items()}
        merged: dict[str, Any] = {}
        for source in self._sources.values():
            merged.update(source)
        self._merged = merged
        return self.data

    def get(self, key: str, default: Any = None) -> Any:
        return self._merged.get(key, default)

    def set(self, key: str, value: Any, owner: str) -> None:
        if owner not in OWNER:
            raise KeyError(f"Unknown configuration owner: {owner}")
        source = self._sources.setdefault(owner, {})
        source[key] = value
        path = self.root / OWNER[owner]
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(source, handle, indent=2, ensure_ascii=False)
            handle.write("\\n")
        temporary.replace(path)
        self._merged[key] = value
