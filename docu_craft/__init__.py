from .document import Document
from .themes import ThemeManager
from .skeletons import SkeletonManager
from .skeletons.manager import register as register_skeleton
from .renderers import register as register_transformer
from .workflow import graph as workflow
from .config import add_extended_store
from .storage import registry, StorageRegistry, Store, StoreKind
from pathlib import Path


def render(
    source: str | Path,
    theme: str = "scholar",
    format: str = "pdf",
    output: str | Path | None = None,
    engine: str | None = None,
    emoji_set: str | None = None,
) -> Path:
    return Document(source).apply_theme(theme).render(
        format=format, output=output, engine=engine, emoji_set=emoji_set
    )


__all__ = [
    "Document",
    "ThemeManager",
    "SkeletonManager",
    "register_transformer",
    "register_skeleton",
    "workflow",
    "add_extended_store",
    "registry",
    "StorageRegistry",
    "Store",
    "StoreKind",
    "render",
]
