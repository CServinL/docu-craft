import markdown
from .base import BaseTransformer
from ..emoji import EmojiManager, replace_emoji
from ..themes.base import resolve_font

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
    priority = 1  # preferred md→? path

    def transform(self, content: str, **options) -> str:
        """
        options:
            emoji_set (str|None)  — name of emoji set to replace unicode emoji
            css (str|None)        — CSS string to embed in <style>
            base_url (str|None)   — base URL for relative links (unused here, passed through)
        """
        body = markdown.markdown(content, extensions=_EXTENSIONS)

        emoji_set = options.get("emoji_set")
        if emoji_set:
            set_dir = EmojiManager.set_dir(emoji_set)
            body = replace_emoji(body, set_dir)

        # If no explicit CSS, generate minimal CSS from style dict
        css = options.get("css", "")
        if not css:
            s = options.get("style", {})
            fonts = s.get("fonts", {})
            body_font   = resolve_font(fonts.get("body",   ["serif"]), "html")
            header_font = resolve_font(fonts.get("header", ["sans-serif"]), "html")
            mono_font   = resolve_font(fonts.get("mono",   ["monospace"]), "html")
            colors = s.get("colors", {})
            css = (
                f"body {{ font-family: {body_font}; font-size: {s.get('font_size', 11)}pt; }}\n"
                f"h1,h2,h3,h4,h5,h6 {{ font-family: {header_font}; }}\n"
                f"code,pre {{ font-family: {mono_font}; }}\n"
                f"body {{ color: {colors.get('body', '#1a1a1a')}; }}\n"
                f"h1,h2,h3 {{ color: {colors.get('heading', '#1a1a2e')}; }}\n"
            )
        style = f"<style>{css}</style>" if css else ""

        return _WRAPPER.format(body=body, style=style)
