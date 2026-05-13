from pathlib import Path
import yaml
from .themes import ThemeManager, Theme
from .skeletons import SkeletonManager, Skeleton
from .workflow import graph as _workflow
from .config import load_settings

_SENTINEL = object()   # distinct from None so callers can pass engine=None explicitly

_BINARY_FMTS = {"pdf"}
_EXT_TO_FMT = {
    ".md":    "md",
    ".html":  "html",
    ".htm":   "html",
    ".pdf":   "pdf",
    ".latex": "latex",
    ".tex":   "latex",
    ".docx":  "docx",
    ".odt":   "odt",
}


class Document:
    def __init__(self, source: str | Path):
        self.source = Path(source)
        self.fmt = _EXT_TO_FMT.get(self.source.suffix.lower(), "md")
        if self.fmt in _BINARY_FMTS:
            self.body = self.source.read_bytes()
            self.frontmatter: dict = {}
        else:
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

        to_fmt = cfg["format"]
        needs_theme = not (self.fmt in _BINARY_FMTS or to_fmt == "md")
        if needs_theme and self._theme is None:
            self._theme = ThemeManager.load(cfg["theme"])

        if output is None:
            output = self.source.with_suffix(f".{to_fmt}")

        theme_opts = {}
        if self._theme:
            theme_opts["style"]     = self._theme.style
            theme_opts["css"]       = self._theme.css
            theme_opts["preamble"]  = self._theme.latex_preamble
            theme_opts["doc_class"] = self._theme.latex_doc_class

        output = Path(output)
        result = _workflow.run(
            self.body,
            from_fmt=self.fmt,
            to_fmt=to_fmt,
            engine=cfg["engine"],
            emoji_set=cfg["emoji_set"],
            base_url=str(self.source.parent),
            output=output,
            **theme_opts,
        )
        if isinstance(result, Path):
            return result
        if isinstance(result, bytes):
            output.write_bytes(result)
        else:
            output.write_text(result, encoding="utf-8")
        return output

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
