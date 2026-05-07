from pathlib import Path
from weasyprint import HTML, CSS
from .base import BaseTransformer


class WeasyprintTransformer(BaseTransformer):
    """HTML → PDF via WeasyPrint."""

    input_fmt = "html"
    output_fmt = "pdf"
    applies_style = False
    priority = 1

    def transform(self, content: str, **options) -> bytes:
        """
        options:
            css (str|None)      — additional CSS string
            base_url (str|None) — base URL for resolving relative assets
            output (Path|None)  — if given, write PDF to this path and return it;
                                  otherwise return raw bytes
        """
        stylesheets = []
        css = options.get("css")
        if css:
            stylesheets.append(CSS(string=css))

        base_url = options.get("base_url")
        pdf_bytes = HTML(string=content, base_url=base_url).write_pdf(
            stylesheets=stylesheets
        )

        output = options.get("output")
        if output:
            Path(output).write_bytes(pdf_bytes)
            return Path(output)

        return pdf_bytes
