from .document import Document
from .themes import ThemeManager
from .skeletons import SkeletonManager
from .renderers import get_renderer
from pathlib import Path


def render(
    source: str | Path,
    theme: str = "scholar",
    format: str = "pdf",
    output: str | Path | None = None,
    engine: str | None = None,
) -> Path:
    return Document(source).apply_theme(theme).render(format=format, output=output, engine=engine)


__all__ = ["Document", "ThemeManager", "SkeletonManager", "get_renderer", "render"]
