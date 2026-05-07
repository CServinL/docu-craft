from pathlib import Path
import yaml
from .themes import ThemeManager, Theme
from .skeletons import SkeletonManager, Skeleton
from .renderers import get_renderer
from .config import load_settings

_SENTINEL = object()   # distinct from None so callers can pass engine=None explicitly


class Document:
    def __init__(self, source: str | Path):
        self.source = Path(source)
        raw = self.source.read_text(encoding="utf-8")
        self.frontmatter, self.body = _split_frontmatter(raw)
        self._theme: Theme | None       = None
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
        format: str  = _SENTINEL,   # type: ignore[assignment]
        output: str | Path | None = None,
        engine: str | None = _SENTINEL,  # type: ignore[assignment]
        theme:  str | None = _SENTINEL,  # type: ignore[assignment]
    ) -> Path:
        cfg = self._resolve_settings(format, engine, theme)

        if self._theme is None:
            self._theme = ThemeManager.load(cfg["theme"])

        if output is None:
            output = self.source.with_suffix(f".{cfg['format']}")

        renderer = get_renderer(cfg["format"], cfg["engine"])
        return renderer.render(self, Path(output))

    # ── internals ────────────────────────────────────────────────────────────

    def _resolve_settings(self, format=_SENTINEL, engine=_SENTINEL, theme=_SENTINEL) -> dict:
        """Merge config layers, lowest → highest priority."""
        # 1. hardcoded defaults + user/project config files
        cfg = load_settings(self.source.parent)

        # 2. document frontmatter
        for key in ("format", "engine", "theme"):
            if key in self.frontmatter:
                cfg[key] = self.frontmatter[key]

        # 3. explicit render() arguments (sentinel means "not passed")
        if format is not _SENTINEL:
            cfg["format"] = format
        if engine is not _SENTINEL:
            cfg["engine"] = engine
        if theme is not _SENTINEL:
            cfg["theme"] = theme

        return cfg


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
