from pathlib import Path

from reportlab.lib.pagesizes import A4          # noqa: F401 — triggers ImportError if missing
from reportlab.platypus import SimpleDocTemplate # noqa: F401

from .base import BaseRenderer

# TODO: implement full ReportLab pipeline
# Rough plan:
#   1. Parse document.body (Markdown AST → ReportLab Flowables)
#   2. Apply document._theme — map theme.meta to ReportLab styles (ParagraphStyle, TableStyle)
#   3. Build SimpleDocTemplate with page size / margins from theme
#   4. doc.build(flowables) → output PDF
#
# ReportLab gives pixel-level control: custom fonts, headers/footers as Flowables,
# vector drawings, precise table layouts — use it when WeasyPrint CSS isn't enough.


class ReportLabPDFRenderer(BaseRenderer):
    def render(self, document, output: Path) -> Path:
        raise NotImplementedError(
            "ReportLabPDFRenderer is not implemented yet.\n"
            "Use engine='weasyprint' in the meantime."
        )
