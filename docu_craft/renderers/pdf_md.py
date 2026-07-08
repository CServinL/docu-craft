"""PDF → Markdown transformer via PyMuPDF.

Extracts text and structure from a PDF, producing clean Markdown with:
- Headings inferred from font size relative to the body text size
- Paragraphs with whitespace normalized
- Tables detected via PyMuPDF's table finder and rendered as real
  `|pipe|table|` markdown, instead of flattening rows into run-on prose
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


def _extract_tables(page) -> list[tuple[float, tuple, str]]:
    """Detect tables on a page and render each as a markdown pipe table.

    PyMuPDF's default "lines" strategy needs actual ruled gridlines, which
    most academic-paper tables don't have (booktabs-style: at most a couple
    of horizontal rules, no vertical lines at all — confirmed against a
    borderless test table not being found under the default strategy).
    "text" strategy detects columns/rows from whitespace and text alignment
    instead, catching both ruled and fully borderless tables.

    Returns (y0, bbox, markdown) tuples: y0 for splicing into reading order
    alongside paragraph blocks, bbox so the caller can skip any text block
    that falls inside it (avoiding duplicating the same content as flattened
    prose right after its table rendering).
    """
    try:
        finder = page.find_tables(vertical_strategy="text", horizontal_strategy="text")
    except Exception:
        return []

    results: list[tuple[float, tuple, str]] = []
    for table in finder.tables:
        rows = [r for r in table.extract() if any((c or "").strip() for c in r)]
        if len(rows) < 2:
            continue
        n_cols = max(len(r) for r in rows)

        def _cell(v: str | None) -> str:
            return (v or "").replace("\n", " ").replace("|", "/").strip()

        def _row(r: list) -> str:
            cells = [_cell(c) for c in r] + [""] * (n_cols - len(r))
            return "| " + " | ".join(cells) + " |"

        lines = [_row(rows[0]), "| " + " | ".join(["---"] * n_cols) + " |"]
        lines.extend(_row(r) for r in rows[1:])
        results.append((table.bbox[1], table.bbox, "\n".join(lines)))
    return results


def _inside_table(block_bbox: tuple, table_bboxes: list[tuple]) -> bool:
    """A text block is part of a detected table if its vertical center
    falls within the table's vertical extent — cheaper and more robust
    than exact rectangle containment, since table cell blocks sometimes
    extend a point or two past the table's own outer bbox."""
    center_y = (block_bbox[1] + block_bbox[3]) / 2
    return any(t[1] - 2 <= center_y <= t[3] + 2 for t in table_bboxes)


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

        tables = _extract_tables(page)
        table_bboxes = [t[1] for t in tables]
        # (y0, content) pairs so tables and paragraphs interleave in the
        # page's real reading order instead of all tables trailing their page
        page_items: list[tuple[float, str]] = [(y0, md) for y0, _bbox, md in tables]

        for block in blocks:
            if _inside_table(block["bbox"], table_bboxes):
                continue  # already rendered as part of a detected table above

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
                page_items.append((block["bbox"][1], f"{'#' * heading_level} {paragraph}"))
            else:
                page_items.append((block["bbox"][1], paragraph))

        page_items.sort(key=lambda item: item[0])
        sections.extend(content for _y0, content in page_items)

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
