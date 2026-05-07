"""Docify storage abstraction.

Three store kinds, searched in priority order (highest first):

    extended  — any filesystem path registered at runtime or via config
    user      — ~/docify/  (personal)
    bundled   — inside the installed package  (lowest, always present)

Every store exposes the same sub-directories:
    <root>/themes/
    <root>/skeletons/
    <root>/emoji-sets/

Managers (ThemeManager, SkeletonManager, EmojiManager) call
StorageRegistry.search(subdir) to get an ordered list of directories
to scan, then take the first hit.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class StoreKind(str, Enum):
    BUNDLED  = "bundled"
    USER     = "user"
    EXTENDED = "extended"

    # sort key: extended first, bundled last
    def _priority(self) -> int:
        return {"extended": 0, "user": 1, "bundled": 2}[self.value]


@dataclass
class Store:
    path: Path
    kind: StoreKind
    name: str = ""
    readonly: bool = False   # True for bundled — writes are rejected

    # ── sub-directories ───────────────────────────────────────────────────
    def themes_dir(self)    -> Path: return self.path / "themes"
    def skeletons_dir(self) -> Path: return self.path / "skeletons"
    def emoji_dir(self)     -> Path: return self.path / "emoji-sets"

    def subdir(self, name: str) -> Path:
        return self.path / name

    def __str__(self) -> str:
        label = f"[{self.name}] " if self.name else ""
        return f"{label}{self.kind.value}:{self.path}"


class StorageRegistry:
    """Ordered registry of asset stores.

    Stores are kept sorted by (kind priority, insertion order).
    Extended stores always come before user, which comes before bundled.
    Within the same kind, later-added stores have higher priority.
    """

    def __init__(self) -> None:
        self._stores: list[Store] = []
        self._extended_seq: int  = 0   # tie-break within extended kind

    def add(
        self,
        path: str | Path,
        kind: StoreKind = StoreKind.EXTENDED,
        name: str = "",
    ) -> Store:
        """Register a store. Returns the created Store object."""
        store = Store(path=Path(path), kind=kind, name=name)
        self._stores.insert(0, store)   # newest first within same kind
        return store

    def remove(self, path: str | Path) -> None:
        p = Path(path)
        self._stores = [s for s in self._stores if s.path != p]

    def all(self) -> list[Store]:
        """All stores, highest priority first."""
        return sorted(self._stores, key=lambda s: s.kind._priority())

    def search(self, subdir: str) -> list[Path]:
        """Return existing sub-directories across all stores, priority order."""
        result = []
        for store in self.all():
            d = store.subdir(subdir)
            if d.is_dir():
                result.append(d)
        return result

    def list_assets(self, subdir: str) -> list[str]:
        """Return deduplicated asset names visible across all stores.
        Higher-priority stores win when names collide.
        """
        seen: dict[str, None] = {}   # ordered set
        for d in self.search(subdir):
            for item in sorted(d.iterdir()):
                if item.name not in seen:
                    seen[item.name] = None
        return list(seen)

    def find_asset(self, subdir: str, name: str) -> Path | None:
        """Return the highest-priority directory containing `name`, or None."""
        for d in self.search(subdir):
            candidate = d / name
            if candidate.exists():
                return candidate
        return None

    def __repr__(self) -> str:
        return f"StorageRegistry({[str(s) for s in self.all()]})"


# ── global registry — initialized in config.py ───────────────────────────────
registry = StorageRegistry()
