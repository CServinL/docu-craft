"""PDF → Markdown transformer via PyMuPDF.

Extracts text and structure from a PDF, producing clean Markdown with:
- Headings inferred from font size relative to the body text size
- Paragraphs with whitespace normalized
- Page breaks optionally marked
- Images optionally extracted to a directory (requires img_dir option)

Requires the [pymupdf] optional extra.
"""

import re
from pathlib import Path

import fitz  # noqa: F401 — triggers ImportError if [pymupdf] not installed

from .base import BaseTransformer


def _infer_heading(span_size: float, body_size: float) -> int | None:
    ratio = span_size / body_size if body_size else 1.0
    if ratio >= 1.8:
        return 1
    if ratio >= 1.4:
        return 2
    if ratio >= 1.15:
        return 3
    return None


def _dominant_size(blocks: list) -> float:
    """Return the most common font size across all spans — the body size."""
    sizes: dict[float, int] = {}
    for b in blocks:
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                s = round(span["size"], 1)
                sizes[s] = sizes.get(s, 0) + len(span["text"])
    return max(sizes, key=sizes.get) if sizes else 11.0


def pdf_to_md(
    content: bytes,
    img_dir: Path | None = None,
    stem: str = "doc",
    page_breaks: bool = False,
) -> str:
    doc = fitz.open(stream=content, filetype="pdf")
    sections: list[str] = []

    for page_num, page in enumerate(doc, start=1):
        data = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        blocks = [b for b in data["blocks"] if b["type"] == 0]  # text blocks only
        body_size = _dominant_size(blocks)

        for block in blocks:
            lines_text = []
            heading_level = None

            for line in block.get("lines", []):
                line_parts = []
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                    size = round(span["size"], 1)
                    h = _infer_heading(size, body_size)
                    if h and heading_level is None:
                        heading_level = h
                    bold = bool(span["flags"] & 2**4)
                    italic = bool(span["flags"] & 2**1)
                    if bold and not heading_level:
                        text = f"**{text}**"
                    elif italic:
                        text = f"*{text}*"
                    line_parts.append(text)
                if line_parts:
                    lines_text.append(" ".join(line_parts))

            if not lines_text:
                continue

            paragraph = " ".join(lines_text)
            paragraph = re.sub(r" {2,}", " ", paragraph)

            if heading_level:
                sections.append(f"{'#' * heading_level} {paragraph}")
            else:
                sections.append(paragraph)

        # Optional image extraction
        if img_dir is not None:
            img_dir.mkdir(parents=True, exist_ok=True)
            for img_idx, img_info in enumerate(page.get_images(), start=1):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                ext = base_image["ext"]
                img_bytes = base_image["image"]
                fname = f"{stem}_p{page_num:03d}_img{img_idx:02d}.{ext}"
                (img_dir / fname).write_bytes(img_bytes)
                sections.append(f"![Figure p{page_num}-{img_idx}]({img_dir / fname})")

        if page_breaks and page_num < len(doc):
            sections.append("\n---\n")

    doc.close()
    return "\n\n".join(sections)


class PdfMdTransformer(BaseTransformer):
    """PDF → Markdown via PyMuPDF (fitz)."""

    input_fmt  = "pdf"
    output_fmt = "md"
    applies_style = False
    priority = 1

    def transform(self, content: bytes, **options) -> str:
        img_dir = options.get("img_dir")
        return pdf_to_md(
            content,
            img_dir=Path(img_dir) if img_dir else None,
            stem=options.get("stem", "doc"),
            page_breaks=options.get("page_breaks", False),
        )
