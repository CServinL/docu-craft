from .document import Document
from .themes import ThemeManager
from .skeletons import SkeletonManager
from .skeletons.manager import register as register_skeleton
from .renderers import get_renderer
from .renderers import register as register_renderer
from pathlib import Path


def render(
    source: str | Path,
    theme: str = "scholar",
    format: str = "pdf",
    output: str | Path | None = None,
    engine: str | None = None,
) -> Path:
    return Document(source).apply_theme(theme).render(format=format, output=output, engine=engine)


__all__ = [
    "Document",
    "ThemeManager",
    "SkeletonManager",
    "get_renderer",
    "register_renderer",
    "register_skeleton",
    "render",
]
