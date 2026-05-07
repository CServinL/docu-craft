from pathlib import Path
import yaml
from .themes import ThemeManager, Theme
from .skeletons import SkeletonManager, Skeleton
from .workflow import graph as _workflow
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
        format:    str        = _SENTINEL,  # type: ignore[assignment]
        output:    str | Path | None = None,
        engine:    str | None = _SENTINEL,  # type: ignore[assignment]
        theme:     str | None = _SENTINEL,  # type: ignore[assignment]
        emoji_set: str | None = _SENTINEL,  # type: ignore[assignment]
    ) -> Path:
        cfg = self._resolve_settings(format, engine, theme, emoji_set)

        if self._theme is None:
            self._theme = ThemeManager.load(cfg["theme"])

        if output is None:
            output = self.source.with_suffix(f".{cfg['format']}")

        theme_opts = {}
        if self._theme:
            theme_opts["css"]             = self._theme.css
            theme_opts["preamble"]        = self._theme.latex_preamble
            theme_opts["doc_class"]       = self._theme.latex_doc_class

        result = _workflow.run(
            self.body,
            from_fmt="md",
            to_fmt=cfg["format"],
            engine=cfg["engine"],
            emoji_set=cfg["emoji_set"],
            base_url=str(self.source.parent),
            output=Path(output),
            **theme_opts,
        )
        return result if isinstance(result, Path) else Path(output)

    # ── internals ────────────────────────────────────────────────────────────

    def _resolve_settings(
        self,
        format    = _SENTINEL,
        engine    = _SENTINEL,
        theme     = _SENTINEL,
        emoji_set = _SENTINEL,
    ) -> dict:
        cfg = load_settings(self.source.parent)

        for key in ("format", "engine", "theme", "emoji_set"):
            if key in self.frontmatter:
                cfg[key] = self.frontmatter[key]

        if format    is not _SENTINEL: cfg["format"]    = format
        if engine    is not _SENTINEL: cfg["engine"]    = engine
        if theme     is not _SENTINEL: cfg["theme"]     = theme
        if emoji_set is not _SENTINEL: cfg["emoji_set"] = emoji_set

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
