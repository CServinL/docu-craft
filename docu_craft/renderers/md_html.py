import markdown
from .base import BaseTransformer
from ..emoji import EmojiManager, replace_emoji

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

        css = options.get("css", "")
        style = f"<style>{css}</style>" if css else ""

        return _WRAPPER.format(body=body, style=style)
