from dataclasses import dataclass, field
from pathlib import Path
import yaml

_CSS_GENERICS = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui"}

# Canonical set of named styles every renderer must register.
# "font" is a key into the theme's fonts dict ("body", "header", "mono").
# Colors reference hex strings; sizes are in points.
_DEFAULT_STYLES = {
    "body": {
        "font": "body", "size": 11, "color": "#1a1a1a",
        "space_after": 10, "line_height": 1.65,
    },
    "heading1": {
        "font": "header", "size": 16, "color": "#1a1a2e", "bold": True,
        "space_before": 24, "space_after": 8,
    },
    "heading2": {
        "font": "header", "size": 13, "color": "#1a1a2e", "bold": True,
        "space_before": 20, "space_after": 6,
    },
    "heading3": {
        "font": "header", "size": 11, "color": "#1a1a2e", "bold": True,
        "space_before": 16, "space_after": 4,
    },
    "heading4": {
        "font": "header", "size": 10, "color": "#333333", "bold": True,
        "space_before": 12, "space_after": 4,
    },
    "heading5": {
        "font": "header", "size": 10, "color": "#555555", "bold": True,
        "space_before": 10, "space_after": 3,
    },
    "heading6": {
        "font": "header", "size": 10, "color": "#555555", "italic": True,
        "space_before": 8, "space_after": 2,
    },
    "code_block": {
        "font": "mono", "size": 9, "background": "#f4f4f4",
        "space_before": 8, "space_after": 12,
    },
    "code_inline": {
        "font": "mono", "size": 9, "background": "#f4f4f4",
    },
    "bold": {
        "font": "body", "bold": True,
    },
    "italic": {
        "font": "body", "italic": True,
    },
    "table_header": {
        "font": "header", "size": 9, "color": "#ffffff",
        "bold": True, "background": "#1a1a2e",
    },
    "table_cell": {
        "font": "body", "size": 9.5,
    },
    "table_cell_alt": {
        "font": "body", "size": 9.5, "background": "#f7f7f9",
    },
    "list_item": {
        "font": "body", "size": 11, "space_after": 4,
    },
    "quote": {
        "font": "body", "size": 10, "color": "#555555", "italic": True,
        "background": "#f9f9fb", "space_before": 10, "space_after": 10,
    },
}

_DEFAULT_STYLE = {
    "fonts": {
        "body":   ["Georgia", "Times New Roman", "serif"],
        "header": ["Arial", "Helvetica", "sans-serif"],
        "mono":   ["Courier New", "Courier", "monospace"],
        "emoji":  ["Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Twemoji Mozilla"],
    },
    "font_size":     11,
    "heading_sizes": [16, 13, 11, 10, 10, 10],
    "line_height":   1.65,
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
    "styles": _DEFAULT_STYLES,
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
    return "Arial"


# Known filesystem paths for emoji fonts, probed at render time.
# Order matches the font list: Linux → macOS → Windows (including WSL2 mount).
_EMOJI_FONT_PATHS = [
    ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",   "Noto Color Emoji"),
    ("/usr/share/fonts/noto/NotoColorEmoji.ttf",            "Noto Color Emoji"),
    ("/System/Library/Fonts/Apple Color Emoji.ttc",         "Apple Color Emoji"),
    ("/mnt/c/Windows/Fonts/seguiemj.ttf",                   "Segoe UI Emoji"),
    ("C:/Windows/Fonts/seguiemj.ttf",                       "Segoe UI Emoji"),
]


def resolve_emoji_css(emoji_font_list: list[str]) -> str:
    """
    Build CSS that makes emoji fonts available to WeasyPrint.

    Emits @font-face rules for every emoji font whose file can be found on
    the current system, then returns a font-family snippet (no braces) that
    can be appended to any existing font-family declaration.
    """
    found: list[tuple[str, str]] = []   # (name, path)
    seen_names: set[str] = set()

    for path, name in _EMOJI_FONT_PATHS:
        if name not in seen_names and Path(path).exists():
            found.append((name, path))
            seen_names.add(name)

    if not found:
        # Fallback: just name the fonts and hope fontconfig finds them
        stack = ", ".join(
            f'"{f}"' if " " in f else f for f in emoji_font_list
        )
        return f"/* emoji fallback (no font file found on this system) */\n/* {stack} */"

    face_rules = []
    for name, path in found:
        quoted = f'"{name}"'
        face_rules.append(
            f'@font-face {{\n'
            f'  font-family: {quoted};\n'
            f'  src: local({quoted}), url("{path}");\n'
            f'}}'
        )

    stack = ", ".join(f'"{name}"' for name, _ in found)
    comment = f"/* emoji fonts resolved on this system: {stack} */"
    return "\n".join([comment] + face_rules)


def resolve_style(style_def: dict, fonts: dict, fmt: str) -> dict:
    """
    Return a concrete style dict with 'font_name' resolved from the font list.
    All other keys from style_def pass through unchanged.
    """
    font_key = style_def.get("font", "body")
    font_list = fonts.get(font_key, ["serif"])
    return {**style_def, "font_name": resolve_font(font_list, fmt)}


@dataclass
class Theme:
    name: str
    style: dict                  # cross-format style properties (includes "styles" sub-dict)
    css: str = ""                # HTML/WeasyPrint-specific
    latex_preamble: str = ""
    latex_doc_class: str = "12pt,a4paper"
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dir(cls, theme_dir: Path) -> "Theme":
        meta_path = theme_dir / "theme.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        # Cross-format style: merge defaults with theme overrides
        style = _deep_merge(_DEFAULT_STYLE, meta.get("style", {}))

        # HTML-specific
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
