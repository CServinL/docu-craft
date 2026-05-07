from pathlib import Path
import yaml
from .themes import ThemeManager, Theme
from .skeletons import SkeletonManager, Skeleton
from .renderers import get_renderer


class Document:
    def __init__(self, source: str | Path):
        self.source = Path(source)
        raw = self.source.read_text(encoding="utf-8")
        self.frontmatter, self.body = _split_frontmatter(raw)
        self._theme: Theme | None    = None
        self._skeleton: Skeleton | None = None

    # --- fluent API ---

    def apply_theme(self, name: str) -> "Document":
        self._theme = ThemeManager.load(name)
        return self

    def apply_skeleton(self, name: str) -> "Document":
        self._skeleton = SkeletonManager.load(name)
        return self

    def validate(self) -> "Document":
        if self._skeleton:
            self._skeleton.validate(self.body)
        return self

    def render(
        self,
        format: str = "pdf",
        output: str | Path | None = None,
        engine: str | None = None,
    ) -> Path:
        if output is None:
            output = self.source.with_suffix(f".{format}")
        renderer = get_renderer(format, engine)
        return renderer.render(self, Path(output))


# ── helpers ──────────────────────────────────────────────────────────────────

def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, parts[2].lstrip("\n")
