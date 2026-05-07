"""Markdown → DOCX transformer via python-docx."""

import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .base import BaseTransformer
from ..themes.base import resolve_font


def _set_cell_bg(cell, hex_color: str):
    """Set table cell background color."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tcPr.append(shd)


def _set_cell_border_bottom(cell, hex_color: str = "E0E0E0"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{side}")
        if side == "bottom":
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "4")
            border.set(qn("w:color"), hex_color)
        else:
            border.set(qn("w:val"), "none")
        tcBorders.append(border)
    tcPr.append(tcBorders)


class MdDocxTransformer(BaseTransformer):
    """Markdown → DOCX."""

    input_fmt = "md"
    output_fmt = "docx"
    applies_style = True
    priority = 1

    def transform(self, content: str, **options) -> bytes:
        self._style = options.get("style", {})
        doc = Document()
        self._apply_style(doc, options)
        self._convert(doc, content)

        output = options.get("output")
        if output:
            doc.save(str(output))
            return Path(output)

        from io import BytesIO
        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _apply_style(self, doc, options):
        s = self._style
        fonts = s.get("fonts", {})
        normal = doc.styles["Normal"]
        normal.font.name = resolve_font(fonts.get("body", ["Calibri"]), "docx")
        normal.font.size = Pt(s.get("font_size", 11))

    def _convert(self, doc, text: str):
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Fenced code block
            if re.match(r"^```", line):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                p = doc.add_paragraph("\n".join(code_lines), style="No Spacing")
                p.runs[0].font.name = "Courier New"
                p.runs[0].font.size = Pt(9)
                i += 1
                continue

            # ATX headings
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = len(m.group(1))
                doc.add_heading(_strip_inline(m.group(2)), level=level)
                i += 1
                continue

            # Table
            if re.match(r"^\|", line):
                rows = []
                while i < len(lines) and re.match(r"^\|", lines[i]):
                    if re.match(r"^\|[-| :]+\|", lines[i]):  # separator row
                        i += 1
                        continue
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                    i += 1
                if rows:
                    cols = max(len(r) for r in rows)
                    table = doc.add_table(rows=len(rows), cols=cols)
                    table.style = "Table Grid"
                    colors = self._style.get("colors", {})
                    heading_bg   = colors.get("heading",      "#1a1a2e").lstrip("#")
                    heading_text = colors.get("heading_text", "#ffffff")
                    row_alt      = colors.get("row_alt",      "#f7f7f9").lstrip("#")
                    border       = colors.get("border",       "#e0e0e0").lstrip("#")
                    ht_rgb = tuple(int(heading_text.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
                    for r_idx, row in enumerate(rows):
                        for c_idx in range(cols):
                            cell_text = row[c_idx] if c_idx < len(row) else ""
                            cell = table.cell(r_idx, c_idx)
                            cell.paragraphs[0].clear()
                            p = cell.paragraphs[0]
                            if r_idx == 0:
                                _set_cell_bg(cell, heading_bg)
                                run = p.add_run(_strip_inline(cell_text))
                                run.bold = True
                                run.font.color.rgb = RGBColor(*ht_rgb)
                                run.font.size = Pt(9)
                            else:
                                if r_idx % 2 == 0:
                                    _set_cell_bg(cell, row_alt)
                                _set_cell_border_bottom(cell, border)
                                _add_inline(p, cell_text)
                                for run in p.runs:
                                    run.font.size = Pt(self._style.get("font_size", 11) - 1.5)
                continue

            # Horizontal rule
            if re.match(r"^[-*_]{3,}\s*$", line):
                doc.add_paragraph("─" * 40)
                i += 1
                continue

            # Unordered list
            if re.match(r"^[-*+]\s+", line):
                while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                    p = doc.add_paragraph(style="List Bullet")
                    _add_inline(p, re.sub(r"^[-*+]\s+", "", lines[i]))
                    i += 1
                continue

            # Ordered list
            if re.match(r"^\d+\.\s+", line):
                while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                    p = doc.add_paragraph(style="List Number")
                    _add_inline(p, re.sub(r"^\d+\.\s+", "", lines[i]))
                    i += 1
                continue

            # Blank line
            if line.strip() == "":
                i += 1
                continue

            # Normal paragraph
            p = doc.add_paragraph()
            _add_inline(p, line)
            i += 1


def _strip_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    return text


def _add_inline(paragraph, text: str):
    """Parse inline markdown and add runs to paragraph."""
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|(.+?)(?=\*\*|\*|`|$))", re.DOTALL)
    for m in pattern.finditer(text):
        if m.group(2):
            run = paragraph.add_run(m.group(2))
            run.bold = True
        elif m.group(3):
            run = paragraph.add_run(m.group(3))
            run.italic = True
        elif m.group(4):
            run = paragraph.add_run(m.group(4))
            run.font.name = "Courier New"
            run.font.size = Pt(9)
        elif m.group(5):
            paragraph.add_run(m.group(5))
