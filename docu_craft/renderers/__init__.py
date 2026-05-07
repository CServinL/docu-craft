from .base import BaseTransformer
from ..workflow import graph

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

# md → latex  (priority 5 — secondary md→? path)
graph.register(
    "md", "latex",
    "docu_craft.renderers.md_latex:MdLatexTransformer",
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
