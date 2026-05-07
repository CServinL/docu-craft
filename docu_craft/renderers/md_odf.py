"""Markdown → ODT transformer via odfpy.

Named paragraph and character styles are registered in doc.styles so they
appear in LibreOffice's Styles panel.  Emoji are passed through by default
and rely on LibreOffice's font fallback to render; pass strip_emoji=True to
remove them when needed.
"""

import re
from io import BytesIO
from pathlib import Path

from odf.opendocument import OpenDocumentText
from odf.style import (
    Style, TextProperties, ParagraphProperties,
    TableCellProperties, TableColumnProperties,
)
from odf.text import H, P, Span, List, ListItem
from odf.table import Table, TableColumn, TableRow, TableCell

from .base import BaseTransformer
from ..themes.base import resolve_style, _DEFAULT_STYLES

_PAGE_WIDTH_CM = 16.0

_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"
    "\U00002300-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U000020E3"
    "]+",
    re.UNICODE,
)

# Paragraph style names (visible in LibreOffice Styles panel)
_PARA = {
    "body":               "DC Body Text",
    "heading1":           "DC Heading 1",
    "heading2":           "DC Heading 2",
    "heading3":           "DC Heading 3",
    "heading4":           "DC Heading 4",
    "heading5":           "DC Heading 5",
    "heading6":           "DC Heading 6",
    "code_block":         "DC Code Block",
    "list_item":          "DC List Item",
    "quote":              "DC Quote",
    "table_header_para":  "DC Table Header Para",
    "table_cell_para":    "DC Table Cell Para",
}

# Character style names
_CHAR = {
    "bold":        "DC Bold",
    "italic":      "DC Italic",
    "code_inline": "DC Code Inline",
}

# Table cell background/border styles (automatic — not user-visible)
_CELL = {
    "header":   "DC Cell Header",
    "even":     "DC Cell Even",
    "odd":      "DC Cell Odd",
}


def _pt_to_cm(pt: float) -> str:
    return f"{pt / 28.3465:.4f}cm"


def _cm(value: float) -> str:
    return f"{value:.4f}cm"


def _list_item(line: str):
    """Return (indent, is_ordered, text) if line is a list item, else None."""
    m = re.match(r'^(\s*)([-*+])\s+(.*)', line)
    if m:
        return len(m.group(1)), False, m.group(3)
    m = re.match(r'^(\s*)\d+\.\s+(.*)', line)
    if m:
        return len(m.group(1)), True, m.group(2)
    return None


class MdOdfTransformer(BaseTransformer):
    """Markdown → ODT (OpenDocument Text)."""

    input_fmt = "md"
    output_fmt = "odt"
    applies_style = True
    priority = 1

    def transform(self, content: str, **options) -> bytes:
        self._style_cfg   = options.get("style", {})
        self._fonts       = self._style_cfg.get("fonts", {})
        self._styles      = self._style_cfg.get("styles", _DEFAULT_STYLES)
        self._colors      = self._style_cfg.get("colors", {})
        self._strip_emoji = options.get("strip_emoji", False)

        doc = OpenDocumentText()
        self._col_cache: dict[int, str] = {}
        self._doc = doc
        self._register_styles(doc)
        self._convert(doc, content)

        output = options.get("output")
        if output:
            doc.save(str(output))
            return Path(output)
        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _clean(self, text: str) -> str:
        if self._strip_emoji:
            return _EMOJI_RE.sub("", text).strip()
        return text

    # ------------------------------------------------------------------
    # Style registration
    # ------------------------------------------------------------------

    def _register_styles(self, doc):
        # Paragraph styles → doc.styles (user-visible)
        para_keys = [
            "body", "heading1", "heading2", "heading3", "heading4",
            "heading5", "heading6", "code_block", "list_item", "quote",
            "table_header", "table_cell",
        ]
        for key in para_keys:
            para_name = _PARA.get(key) or _PARA.get("body")
            sd = resolve_style(self._styles.get(key, {}), self._fonts, "odf")
            self._add_para_style(doc, para_name, sd)

        # Dedicated paragraph styles for inside table cells.
        # Strip 'background' — cell background comes from the table-cell style,
        # not from TextProperties (which would only cover the text span).
        th_sd = {k: v for k, v in
                 resolve_style(self._styles.get("table_header", {}), self._fonts, "odf").items()
                 if k != "background"}
        tc_sd = {k: v for k, v in
                 resolve_style(self._styles.get("table_cell", {}), self._fonts, "odf").items()
                 if k != "background"}
        self._add_para_style(doc, _PARA["table_header_para"], th_sd)
        self._add_para_style(doc, _PARA["table_cell_para"],   tc_sd)

        # Character styles → doc.styles (user-visible)
        for key, name in _CHAR.items():
            sd = resolve_style(self._styles.get(key, {}), self._fonts, "odf")
            self._add_char_style(doc, name, sd)

        # Table cell background styles → automaticstyles (not user-visible)
        border_clr = self._colors.get("border", "#e0e0e0")
        border_rule = f"0.05pt solid {border_clr}"
        header_bg = self._styles.get("table_header", {}).get("background", "#1a1a2e")
        alt_bg    = self._styles.get("table_cell_alt", {}).get("background", "#f7f7f9")

        for name, bg, use_border in [
            (_CELL["header"], header_bg,  False),
            (_CELL["even"],   alt_bg,     True),
            (_CELL["odd"],    None,        True),
        ]:
            s = Style(name=name, family="table-cell")
            cp: dict = {"padding": "0.1cm"}
            if bg:
                cp["backgroundcolor"] = bg
            if use_border:
                cp["borderbottom"] = border_rule
            s.addElement(TableCellProperties(**cp))
            doc.automaticstyles.addElement(s)

    def _add_para_style(self, doc, name: str, sd: dict):
        style = Style(name=name, family="paragraph")
        pp: dict = {}
        if "space_before" in sd:
            pp["margintop"] = _pt_to_cm(sd["space_before"])
        if "space_after" in sd:
            pp["marginbottom"] = _pt_to_cm(sd["space_after"])
        if pp:
            style.addElement(ParagraphProperties(**pp))
        tp: dict = {}
        if sd.get("font_name"):
            tp["fontname"] = sd["font_name"]
        if "size" in sd:
            tp["fontsize"] = f"{sd['size']}pt"
        if sd.get("color"):
            tp["color"] = sd["color"]
        if sd.get("bold"):
            tp["fontweight"] = "bold"
        if sd.get("italic"):
            tp["fontstyle"] = "italic"
        if sd.get("background"):
            tp["backgroundcolor"] = sd["background"]
        if tp:
            style.addElement(TextProperties(**tp))
        doc.styles.addElement(style)

    def _add_char_style(self, doc, name: str, sd: dict):
        style = Style(name=name, family="text")
        tp: dict = {}
        if sd.get("font_name"):
            tp["fontname"] = sd["font_name"]
        if "size" in sd:
            tp["fontsize"] = f"{sd['size']}pt"
        if sd.get("color"):
            tp["color"] = sd["color"]
        if sd.get("bold"):
            tp["fontweight"] = "bold"
        if sd.get("italic"):
            tp["fontstyle"] = "italic"
        if sd.get("background"):
            tp["backgroundcolor"] = sd["background"]
        if tp:
            style.addElement(TextProperties(**tp))
        doc.styles.addElement(style)

    def _col_style(self, cols: int) -> str:
        if cols in self._col_cache:
            return self._col_cache[cols]
        name = f"DC Col {cols}"
        s = Style(name=name, family="table-column")
        s.addElement(TableColumnProperties(columnwidth=_cm(_PAGE_WIDTH_CM / cols)))
        self._doc.automaticstyles.addElement(s)
        self._col_cache[cols] = name
        return name

    # ------------------------------------------------------------------
    # Content conversion
    # ------------------------------------------------------------------

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
                p = P(stylename=_PARA["code_block"])
                p.addText("\n".join(code_lines))
                doc.text.addElement(p)
                i += 1
                continue

            # ATX headings
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = min(len(m.group(1)), 6)
                h = H(
                    outlinelevel=level,
                    stylename=_PARA[f"heading{level}"],
                    text=self._clean(_strip_inline(m.group(2))),
                )
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
                    self._add_table(doc, rows)
                continue

            # Blockquote
            if line.startswith("> "):
                p = P(stylename=_PARA["quote"])
                _add_inline_odf(p, line[2:], _CHAR)
                doc.text.addElement(p)
                i += 1
                continue

            # List — ordered or unordered, any indent level
            if _list_item(line) is not None:
                base_indent = _list_item(line)[0]
                items, i = self._collect_list(lines, i, base_indent)
                doc.text.addElement(self._build_list(items))
                continue

            # Blank line
            if line.strip() == "":
                i += 1
                continue

            # Normal paragraph
            p = P(stylename=_PARA["body"])
            _add_inline_odf(p, line, _CHAR)
            doc.text.addElement(p)
            i += 1

    def _collect_list(self, lines, start, base_indent):
        """Collect list items at base_indent, recursing into deeper levels."""
        items = []
        i = start
        while i < len(lines):
            parsed = _list_item(lines[i])
            if parsed is None:
                break
            indent, is_ordered, text = parsed
            if indent < base_indent:
                break
            if indent > base_indent:
                # Child block — attach to last item
                if items:
                    children, i = self._collect_list(lines, i, indent)
                    items[-1] = (*items[-1][:3], children)
                else:
                    i += 1
                continue
            items.append((indent, is_ordered, text, []))
            i += 1
        return items, i

    def _build_list(self, items) -> List:
        lst = List()
        for _, _, text, children in items:
            item = ListItem()
            p = P(stylename=_PARA["list_item"])
            _add_inline_odf(p, text, _CHAR)
            item.addElement(p)
            if children:
                item.addElement(self._build_list(children))
            lst.addElement(item)
        return lst

    def _add_table(self, doc, rows):
        cols = max(len(r) for r in rows)
        col_style = self._col_style(cols)
        table = Table()
        for _ in range(cols):
            table.addElement(TableColumn(stylename=col_style))

        header_clr = self._styles.get("table_header", {}).get("color", "#ffffff")

        for r_idx, row in enumerate(rows):
            tr = TableRow()
            for c_idx in range(cols):
                cell_text = row[c_idx] if c_idx < len(row) else ""
                if r_idx == 0:
                    tc = TableCell(stylename=_CELL["header"])
                    p = P(stylename=_PARA["table_header_para"])
                    span = Span(stylename=_CHAR["bold"],
                                text=self._clean(_strip_inline(cell_text)))
                    p.addElement(span)
                else:
                    cell_style = _CELL["even"] if r_idx % 2 == 0 else _CELL["odd"]
                    tc = TableCell(stylename=cell_style)
                    p = P(stylename=_PARA["table_cell_para"])
                    _add_inline_odf(p, cell_text, _CHAR)
                tc.addElement(p)
                tr.addElement(tc)
            table.addElement(tr)
        doc.text.addElement(table)


# ------------------------------------------------------------------
# Inline helpers
# ------------------------------------------------------------------

def _strip_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    return text


def _add_inline_odf(parent, text: str, char_names: dict):
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|([^*`]+))")
    for m in pattern.finditer(text):
        if m.group(2):
            parent.addElement(Span(stylename=char_names["bold"], text=m.group(2)))
        elif m.group(3):
            parent.addElement(Span(stylename=char_names["italic"], text=m.group(3)))
        elif m.group(4):
            parent.addElement(Span(stylename=char_names["code_inline"], text=m.group(4)))
        elif m.group(5):
            parent.addText(m.group(5))
