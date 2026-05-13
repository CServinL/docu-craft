from .base import BaseTransformer
from ..workflow import graph

# pdf → md  (requires [pymupdf] extra)
graph.register(
    "pdf", "md",
    "docu_craft.renderers.pdf_md:PdfMdTransformer",
    package="pymupdf",
    install='pip install "docu-craft[pymupdf]"',
    priority=1,
)

# html → md  (requires [html] extra: beautifulsoup4 + html2text)
graph.register(
    "html", "md",
    "docu_craft.renderers.html_md:HtmlMdTransformer",
    package="beautifulsoup4 html2text",
    install='pip install "docu-craft[html]"',
    priority=1,
)

# md → html  (priority 1 — preferred md→? path)
graph.register(
    "md", "html",
    "docu_craft.renderers.md_html:MdHtmlTransformer",
    priority=1,
)

# html → pdf via weasyprint  (priority 1)
graph.register(
    "html", "pdf",
    "docu_craft.renderers.weasyprint_pdf:WeasyprintTransformer",
    engine="weasyprint",
    package="weasyprint",
    install="pip install weasyprint",
    priority=1,
)

# html → pdf default (same transformer, no engine tag)
graph.register(
    "html", "pdf",
    "docu_craft.renderers.weasyprint_pdf:WeasyprintTransformer",
    package="weasyprint",
    install="pip install weasyprint",
    priority=1,
)

# html → pdf via reportlab
graph.register(
    "html", "pdf",
    "docu_craft.renderers.reportlab_pdf:ReportLabTransformer",
    engine="reportlab",
    package="reportlab",
    install='pip install "docu-craft[reportlab]"',
    priority=5,
)

# md → docx
graph.register(
    "md", "docx",
    "docu_craft.renderers.md_docx:MdDocxTransformer",
    package="python-docx",
    install='pip install "docu-craft[docx]"',
    priority=1,
)

# md → odt (OpenDocument Text)
graph.register(
    "md", "odt",
    "docu_craft.renderers.md_odf:MdOdfTransformer",
    package="odfpy",
    install="pip install odfpy",
    priority=1,
)

# md → latex  (registered twice: once as default for direct format requests,
#              once tagged engine=latex for path preference routing)
graph.register(
    "md", "latex",
    "docu_craft.renderers.md_latex:MdLatexTransformer",
    priority=5,
)
graph.register(
    "md", "latex",
    "docu_craft.renderers.md_latex:MdLatexTransformer",
    engine="latex",
    priority=5,
)

# latex → pdf  (priority 1)
graph.register(
    "latex", "pdf",
    "docu_craft.renderers.latex_pdf:LatexPdfTransformer",
    engine="latex",
    priority=1,
)


def register(
    from_fmt: str,
    to_fmt: str,
    module_path: str,
    engine: str | None = None,
    package: str | None = None,
    install: str | None = None,
) -> None:
    graph.register(from_fmt, to_fmt, module_path, engine, package, install)


def run(content, from_fmt: str, to_fmt: str, engine: str | None = None, **options):
    return graph.run(content, from_fmt, to_fmt, engine, **options)


__all__ = ["BaseTransformer", "graph", "register", "run"]
