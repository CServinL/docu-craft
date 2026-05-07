"""LaTeX → PDF transformer via pdflatex/xelatex/lualatex."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import BaseTransformer


class LatexPdfTransformer(BaseTransformer):
    """LaTeX (.tex source) → PDF by shelling out to a LaTeX engine."""

    input_fmt = "latex"
    output_fmt = "pdf"
    applies_style = False
    priority = 1

    def transform(self, content: str, **options) -> bytes | Path:
        """
        options:
            latex_engine (str)  — 'pdflatex' (default), 'xelatex', or 'lualatex'
            output (Path|None)  — write PDF here and return the Path; else return bytes
        """
        engine = options.get("latex_engine", "pdflatex")
        if not shutil.which(engine):
            raise RuntimeError(
                f"LaTeX engine '{engine}' not found. "
                f"Install a TeX distribution (e.g. TeX Live) and make sure '{engine}' is on PATH."
            )

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            tex_file = tmp / "doc.tex"
            tex_file.write_text(content, encoding="utf-8")

            # Run twice so cross-references (TOC, labels) resolve
            for _ in range(2):
                result = subprocess.run(
                    [engine, "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"{engine} failed:\n{result.stdout[-3000:]}"
                    )

            pdf_bytes = (tmp / "doc.pdf").read_bytes()

        output = options.get("output")
        if output:
            Path(output).write_bytes(pdf_bytes)
            return Path(output)

        return pdf_bytes
