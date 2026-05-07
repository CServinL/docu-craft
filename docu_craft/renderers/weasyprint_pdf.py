from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from .base import BaseRenderer
from ..emoji import EmojiManager, replace_emoji

_MD_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "attr_list"]

_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"></head>
<body>
{body}
</body>
</html>
"""


class WeasyPrintPDFRenderer(BaseRenderer):
    def render(self, document, output: Path, emoji_set: str | None = None) -> Path:
        html_body = markdown.markdown(document.body, extensions=_MD_EXTENSIONS)

        if emoji_set:
            set_dir = EmojiManager.set_dir(emoji_set)
            html_body = replace_emoji(html_body, set_dir)

        full_html = _HTML_WRAPPER.format(body=html_body)

        stylesheets = []
        if document._theme:
            stylesheets.append(CSS(string=document._theme.css))

        HTML(
            string=full_html,
            base_url=str(document.source.parent),
        ).write_pdf(str(output), stylesheets=stylesheets)

        return output
