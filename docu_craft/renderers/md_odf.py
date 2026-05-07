"""Markdown → ODF (ODT) transformer via odfpy."""

import re
from io import BytesIO
from pathlib import Path

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableCellProperties
from odf.text import H, P, Span, List, ListItem
from odf.table import Table, TableColumn, TableRow, TableCell

from .base import BaseTransformer
from ..themes.base import resolve_font


class MdOdfTransformer(BaseTransformer):
    """Markdown → ODT (OpenDocument Text)."""

    input_fmt = "md"
    output_fmt = "odf"
    applies_style = True
    priority = 1

    def transform(self, content: str, **options) -> bytes:
        self._style = options.get("style", {})
        self._colors = self._style.get("colors", {})
        doc = OpenDocumentText()
        self._add_styles(doc)
        self._convert(doc, content)

        output = options.get("output")
        if output:
            doc.save(str(output))
            return Path(output)

        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _add_styles(self, doc):
        fonts = self._style.get("fonts", {})
        body_font   = resolve_font(fonts.get("body",   ["Georgia"]),      "odf")
        header_font = resolve_font(fonts.get("header", ["Arial"]),        "odf")
        mono_font   = resolve_font(fonts.get("mono",   ["Courier New"]),  "odf")
        font_size   = f"{self._style.get('font_size', 11)}pt"

        code_style = Style(name="Code", family="text")
        code_style.addElement(TextProperties(fontname=mono_font, fontsize="9pt"))
        doc.automaticstyles.addElement(code_style)

        bold_style = Style(name="Bold", family="text")
        bold_style.addElement(TextProperties(fontweight="bold", fontname=body_font))
        doc.automaticstyles.addElement(bold_style)

        italic_style = Style(name="Italic", family="text")
        italic_style.addElement(TextProperties(fontstyle="italic", fontname=body_font))
        doc.automaticstyles.addElement(italic_style)

        heading_bg   = self._colors.get("heading",      "#1a1a2e")
        heading_text = self._colors.get("heading_text", "#ffffff")
        row_alt      = self._colors.get("row_alt",      "#f7f7f9")
        border       = self._colors.get("border",       "#e0e0e0")
        border_rule  = f"0.05pt solid {border}"

        th_style = Style(name="TableHeader", family="table-cell")
        th_style.addElement(TableCellProperties(backgroundcolor=heading_bg, padding="0.1cm"))
        doc.automaticstyles.addElement(th_style)

        th_text = Style(name="TableHeaderText", family="text")
        th_text.addElement(TextProperties(color=heading_text, fontweight="bold", fontsize="9pt"))
        doc.automaticstyles.addElement(th_text)

        td_even_style = Style(name="TableCellEven", family="table-cell")
        td_even_style.addElement(TableCellProperties(backgroundcolor=row_alt, padding="0.1cm",
                                                      borderbottom=border_rule))
        doc.automaticstyles.addElement(td_even_style)

        td_odd_style = Style(name="TableCellOdd", family="table-cell")
        td_odd_style.addElement(TableCellProperties(padding="0.1cm", borderbottom=border_rule))
        doc.automaticstyles.addElement(td_odd_style)

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
                p = P(stylename="Preformatted Text")
                p.addText("\n".join(code_lines))
                doc.text.addElement(p)
                i += 1
                continue

            # ATX headings
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = min(len(m.group(1)), 6)
                h = H(outlinelevel=level, text=_strip_inline(m.group(2)))
                doc.text.addElement(h)
                i += 1
                continue

            # Table
            if re.match(r"^\|", line):
                rows = []
                while i < len(lines) and re.match(r"^\|", lines[i]):
                    if re.match(r"^\|[-| :]+\|", lines[i]):
                        i += 1
                        continue
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                    i += 1
                if rows:
                    cols = max(len(r) for r in rows)
                    table = Table()
                    for _ in range(cols):
                        table.addElement(TableColumn())
                    for r_idx, row in enumerate(rows):
                        tr = TableRow()
                        for c_idx in range(cols):
                            cell_text = row[c_idx] if c_idx < len(row) else ""
                            if r_idx == 0:
                                tc = TableCell(stylename="TableHeader")
                                p = P()
                                p.addElement(Span(stylename="TableHeaderText",
                                                  text=_strip_inline(cell_text)))
                            else:
                                cell_style = "TableCellEven" if r_idx % 2 == 0 else "TableCellOdd"
                                tc = TableCell(stylename=cell_style)
                                p = P()
                                _add_inline_odf(p, cell_text)
                            tc.addElement(p)
                            tr.addElement(tc)
                        table.addElement(tr)
                    doc.text.addElement(table)
                continue

            # Unordered list
            if re.match(r"^[-*+]\s+", line):
                lst = List()
                while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                    item_text = re.sub(r"^[-*+]\s+", "", lines[i])
                    item = ListItem()
                    p = P()
                    _add_inline_odf(p, item_text)
                    item.addElement(p)
                    lst.addElement(item)
                    i += 1
                doc.text.addElement(lst)
                continue

            # Blank line
            if line.strip() == "":
                i += 1
                continue

            # Normal paragraph
            p = P()
            _add_inline_odf(p, line)
            doc.text.addElement(p)
            i += 1


def _strip_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    return text


def _add_inline_odf(parent, text: str):
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|([^*`]+))")
    for m in pattern.finditer(text):
        if m.group(2):
            span = Span(stylename="Bold", text=m.group(2))
            parent.addElement(span)
        elif m.group(3):
            span = Span(stylename="Italic", text=m.group(3))
            parent.addElement(span)
        elif m.group(4):
            span = Span(stylename="Code", text=m.group(4))
            parent.addElement(span)
        elif m.group(5):
            parent.addText(m.group(5))
