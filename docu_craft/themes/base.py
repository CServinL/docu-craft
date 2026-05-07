from dataclasses import dataclass, field
from pathlib import Path
import yaml

_CSS_GENERICS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui"}

_DEFAULT_STYLE = {
    "fonts": {
        "body":   ["Georgia", "Times New Roman", "serif"],
        "header": ["Arial", "Helvetica", "sans-serif"],
        "mono":   ["Courier New", "Courier", "monospace"],
    },
    "font_size":   11,
    "line_height": 1.65,
    "page_margin": "2.5cm",
    "page_size":   "a4",
    "colors": {
        "body":         "#1a1a1a",
        "heading":      "#1a1a2e",
        "heading_text": "#ffffff",
        "accent":       "#1a1a2e",
        "border":       "#e0e0e0",
        "row_alt":      "#f7f7f9",
        "code_bg":      "#f4f4f4",
    },
}


def resolve_font(font_list: list[str], fmt: str) -> str:
    """
    Resolve a font list for a given output format.
    - html/css : joins as CSS font stack  ("Georgia, Times New Roman, serif")
    - other    : first non-generic name   ("Georgia")
    """
    if fmt in ("html", "css"):
        return ", ".join(f'"{f}"' if " " in f else f for f in font_list)
    for f in font_list:
        if f.lower() not in _CSS_GENERICS:
            return f
    return "Arial"  # last-resort fallback


@dataclass
class Theme:
    name: str
    style: dict                  # cross-format style properties
    css: str = ""                # HTML/WeasyPrint-specific
    latex_preamble: str = ""
    latex_doc_class: str = "12pt,a4paper"
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dir(cls, theme_dir: Path) -> "Theme":
        meta_path     = theme_dir / "theme.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        # Cross-format style: merge defaults with theme overrides
        style = _deep_merge(_DEFAULT_STYLE, meta.get("style", {}))

        # HTML-specific: css file specified in theme.yaml or default style.css
        css_file = meta.get("html", {}).get("css", "style.css")
        css_path = theme_dir / css_file
        css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

        # LaTeX-specific
        latex_cfg = meta.get("latex", {})
        doc_class = latex_cfg.get("doc_class", "12pt,a4paper")
        preamble_file = latex_cfg.get("preamble", "latex/preamble.tex")
        preamble_path = theme_dir / preamble_file
        preamble = preamble_path.read_text(encoding="utf-8") if preamble_path.exists() else ""

        return cls(
            name=theme_dir.name,
            style=style,
            css=css,
            latex_preamble=preamble,
            latex_doc_class=doc_class,
            meta=meta,
        )


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
