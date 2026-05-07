from .base import BaseTransformer
from ..workflow import graph

# md → html
graph.register(
    "md", "html",
    "docu_craft.renderers.md_html:MdHtmlTransformer",
)

# html → pdf (weasyprint)
graph.register(
    "html", "pdf",
    "docu_craft.renderers.weasyprint_pdf:WeasyprintTransformer",
    engine="weasyprint",
    package="weasyprint",
    install="pip install weasyprint",
)

# html → pdf (default, same transformer)
graph.register(
    "html", "pdf",
    "docu_craft.renderers.weasyprint_pdf:WeasyprintTransformer",
    package="weasyprint",
    install="pip install weasyprint",
)

# html → pdf (reportlab)
graph.register(
    "html", "pdf",
    "docu_craft.renderers.reportlab_pdf:ReportLabTransformer",
    engine="reportlab",
    package="reportlab",
    install='pip install "docu-craft[reportlab]"',
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
