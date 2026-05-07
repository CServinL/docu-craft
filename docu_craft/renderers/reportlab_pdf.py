from reportlab.lib.pagesizes import A4          # noqa: F401 — triggers ImportError if missing
from reportlab.platypus import SimpleDocTemplate # noqa: F401

from .base import BaseTransformer


class ReportLabTransformer(BaseTransformer):
    """HTML → PDF via ReportLab (not yet implemented)."""

    input_fmt = "html"
    output_fmt = "pdf"

    def transform(self, content: str, **options):
        raise NotImplementedError(
            "ReportLab transformer is not implemented yet.\n"
            "Use engine='weasyprint' in the meantime."
        )
