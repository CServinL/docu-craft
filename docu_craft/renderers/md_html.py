"""Markdown → HTML transformer.

When a theme CSS file is provided it is embedded directly.  When no CSS is
available a stylesheet is generated from the theme's styles dict so that
headless/no-theme usage still produces consistent output.
"""

import markdown
from .base import BaseTransformer
from ..emoji import EmojiManager, replace_emoji
from ..themes.base import resolve_font, resolve_style, resolve_emoji_css, _DEFAULT_STYLES

_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "attr_list"]

_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8">{style}</head>
<body>
{body}
</body>
</html>
"""


class MdHtmlTransformer(BaseTransformer):
    """Markdown → HTML."""

    input_fmt = "md"
    output_fmt = "html"
    applies_style = True
    priority = 1

    def transform(self, content: str, **options) -> str:
        body = markdown.markdown(content, extensions=_EXTENSIONS)

        emoji_set = options.get("emoji_set")
        if emoji_set:
            set_dir = EmojiManager.set_dir(emoji_set)
            body = replace_emoji(body, set_dir)

        css = options.get("css", "")
        if not css:
            css = _generate_css(options.get("style", {}))
        else:
            # Prepend @font-face rules for emoji even when using a theme CSS file
            style_cfg = options.get("style", {})
            emoji_list = style_cfg.get("fonts", {}).get("emoji", [])
            if emoji_list:
                css = resolve_emoji_css(emoji_list) + "\n" + css

        style = f"<style>{css}</style>" if css else ""
        return _WRAPPER.format(body=body, style=style)


def _generate_css(style_cfg: dict) -> str:
    """Build a CSS stylesheet from the theme's styles dict."""
    fonts        = style_cfg.get("fonts", {})
    styles       = style_cfg.get("styles", _DEFAULT_STYLES)
    colors       = style_cfg.get("colors", {})
    margin       = style_cfg.get("page_margin", "2.5cm")
    lh           = style_cfg.get("line_height", 1.65)
    emoji_list   = fonts.get("emoji", [])
    emoji_suffix = (
        ", " + ", ".join(f'"{f}"' if " " in f else f for f in emoji_list)
        if emoji_list else ""
    )
    emoji_face   = resolve_emoji_css(emoji_list) + "\n" if emoji_list else ""

    def sd(key):
        return resolve_style(styles.get(key, {}), fonts, "html")

    body_s = sd("body")
    h1_s   = sd("heading1")
    h2_s   = sd("heading2")
    h3_s   = sd("heading3")
    h4_s   = sd("heading4")
    h5_s   = sd("heading5")
    h6_s   = sd("heading6")
    code_block_s  = sd("code_block")
    code_inline_s = sd("code_inline")
    th_s   = sd("table_header")
    td_s   = sd("table_cell")
    td_alt = sd("table_cell_alt")
    li_s   = sd("list_item")
    q_s    = sd("quote")
    border_clr = colors.get("border", "#e0e0e0")

    def _font(s):
        return s.get("font_name", "serif")

    def _size(s, fallback=11):
        return s.get("size", fallback)

    def _color(s, fallback="inherit"):
        return s.get("color") or fallback

    def _bg(s, fallback="transparent"):
        return s.get("background") or fallback

    lines = [
        emoji_face,
        "@page {",
        f"  margin: {margin};",
        "  size: A4;",
        "}",
        "",
        "body {",
        f"  font-family: {_font(body_s)}{emoji_suffix};",
        f"  font-size: {_size(body_s)}pt;",
        f"  line-height: {lh};",
        f"  color: {_color(body_s, '#1a1a1a')};",
        "}",
        "",
    ]

    for level, hs in enumerate([h1_s, h2_s, h3_s, h4_s, h5_s, h6_s], start=1):
        lines += [
            f"h{level} {{",
            f"  font-family: {_font(hs)};",
            f"  font-size: {_size(hs)}pt;",
            f"  color: {_color(hs, '#1a1a2e')};",
            f"  font-weight: {'bold' if hs.get('bold', True) else 'normal'};",
            f"  margin-top: {hs.get('space_before', 16)}pt;",
            f"  margin-bottom: {hs.get('space_after', 6)}pt;",
            "}",
            "",
        ]

    lines += [
        "p {",
        f"  margin: 0 0 {body_s.get('space_after', 10)}pt 0;",
        "}",
        "",
        "pre {",
        f"  font-family: {_font(code_block_s)};",
        f"  font-size: {_size(code_block_s, 9)}pt;",
        f"  background: {_bg(code_block_s, '#f4f4f4')};",
        "  padding: 10px 14px;",
        "  border-left: 3px solid " + colors.get("heading", "#1a1a2e") + ";",
        f"  margin: {code_block_s.get('space_before', 8)}pt 0 {code_block_s.get('space_after', 12)}pt 0;",
        "  overflow-x: auto;",
        "}",
        "",
        "code {",
        f"  font-family: {_font(code_inline_s)};",
        f"  font-size: {_size(code_inline_s, 9)}pt;",
        f"  background: {_bg(code_inline_s, '#f4f4f4')};",
        "  padding: 1px 5px;",
        "  border-radius: 3px;",
        "}",
        "pre code { background: none; padding: 0; }",
        "",
        "table {",
        "  border-collapse: collapse;",
        "  width: 100%;",
        "  margin: 12px 0;",
        f"  font-family: {_font(td_s)};",
        f"  font-size: {_size(td_s, 9.5)}pt;",
        "}",
        "",
        "th {",
        f"  background: {_bg(th_s, '#1a1a2e')};",
        f"  color: {_color(th_s, '#ffffff')};",
        f"  font-family: {_font(th_s)};",
        f"  font-size: {_size(th_s, 9)}pt;",
        "  font-weight: bold;",
        "  padding: 6px 10px;",
        "  text-align: left;",
        "}",
        "",
        "td {",
        f"  font-family: {_font(td_s)};",
        f"  font-size: {_size(td_s, 9.5)}pt;",
        "  padding: 5px 10px;",
        f"  border-bottom: 1px solid {border_clr};",
        "  vertical-align: top;",
        "}",
        f"tr:nth-child(even) td {{ background: {_bg(td_alt, '#f7f7f9')}; }}",
        "",
        "ul, ol {",
        f"  font-family: {_font(li_s)};",
        f"  font-size: {_size(li_s)}pt;",
        "  margin: 6px 0 10px 0;",
        "  padding-left: 22px;",
        "}",
        "",
        "blockquote {",
        f"  font-family: {_font(q_s)};",
        f"  font-size: {_size(q_s, 10)}pt;",
        f"  color: {_color(q_s, '#555555')};",
        f"  background: {_bg(q_s, '#f9f9fb')};",
        f"  border-left: 3px solid {colors.get('heading', '#1a1a2e')};",
        "  margin: 14px 0;",
        "  padding: 6px 14px;",
        "  font-style: italic;",
        "}",
    ]

    return "\n".join(lines)
