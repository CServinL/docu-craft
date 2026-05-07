"""Markdown → LaTeX transformer."""

import re
from .base import BaseTransformer

_DOC_TEMPLATE = r"""\documentclass[{doc_class}]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{hyperref}}
\usepackage{{listings}}
\usepackage{{amsmath}}
{preamble}
\begin{{document}}
{body}
\end{{document}}
"""

_SECTION_CMDS = [
    "section", "subsection", "subsubsection",
    "paragraph", "subparagraph",
]


class MdLatexTransformer(BaseTransformer):
    """Markdown → LaTeX (.tex source)."""

    input_fmt = "md"
    output_fmt = "latex"

    def transform(self, content: str, **options) -> str:
        """
        options:
            doc_class (str)   — LaTeX document class option, e.g. '12pt,a4paper'
            preamble  (str)   — extra LaTeX preamble lines
            title     (str)   — document title
            author    (str)   — document author
            date      (str)   — document date (default: \\today)
        """
        body = self._convert(content)

        title  = options.get("title", "")
        author = options.get("author", "")
        date   = options.get("date", r"\today")
        if title:
            maketitle = f"\\title{{{_esc(title)}}}\n\\author{{{_esc(author)}}}\n\\date{{{date}}}\n\\maketitle\n"
        else:
            maketitle = ""

        return _DOC_TEMPLATE.format(
            doc_class=options.get("doc_class", "12pt,a4paper"),
            preamble=options.get("preamble", ""),
            body=maketitle + body,
        )

    def _convert(self, text: str) -> str:
        lines = text.split("\n")
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Fenced code block
            fence = re.match(r"^```(\w*)", line)
            if fence:
                lang = fence.group(1)
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code = "\n".join(code_lines)
                if lang:
                    out.append(f"\\begin{{lstlisting}}[language={lang}]\n{code}\n\\end{{lstlisting}}")
                else:
                    out.append(f"\\begin{{verbatim}}\n{code}\n\\end{{verbatim}}")
                i += 1
                continue

            # ATX headings
            m = re.match(r"^(#{1,5})\s+(.*)", line)
            if m:
                level = len(m.group(1)) - 1
                title = self._inline(m.group(2))
                cmd = _SECTION_CMDS[level]
                out.append(f"\\{cmd}{{{title}}}")
                i += 1
                continue

            # Horizontal rule
            if re.match(r"^[-*_]{3,}\s*$", line):
                out.append(r"\noindent\rule{\linewidth}{0.4pt}")
                i += 1
                continue

            # Unordered list item
            if re.match(r"^[-*+]\s+", line):
                items = []
                while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                    items.append("  \\item " + self._inline(re.sub(r"^[-*+]\s+", "", lines[i])))
                    i += 1
                out.append("\\begin{itemize}\n" + "\n".join(items) + "\n\\end{itemize}")
                continue

            # Ordered list item
            if re.match(r"^\d+\.\s+", line):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                    items.append("  \\item " + self._inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                    i += 1
                out.append("\\begin{enumerate}\n" + "\n".join(items) + "\n\\end{enumerate}")
                continue

            # Blockquote
            if line.startswith("> "):
                quote_lines = []
                while i < len(lines) and lines[i].startswith("> "):
                    quote_lines.append(self._inline(lines[i][2:]))
                    i += 1
                out.append("\\begin{quote}\n" + " ".join(quote_lines) + "\n\\end{quote}")
                continue

            # Blank line → paragraph break
            if line.strip() == "":
                out.append("")
                i += 1
                continue

            out.append(self._inline(line))
            i += 1

        return "\n".join(out)

    def _inline(self, text: str) -> str:
        # Inline code (before bold/italic so backticks aren't mangled)
        text = re.sub(r"`([^`]+)`", lambda m: r"\texttt{" + _esc(m.group(1)) + "}", text)
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
        text = re.sub(r"__(.+?)__",     r"\\textbf{\1}", text)
        # Italic
        text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)
        text = re.sub(r"_(.+?)_",   r"\\textit{\1}", text)
        # Links
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\\href{\2}{\1}", text)
        # Escape special LaTeX chars in plain text runs
        text = _esc_plain(text)
        return text


def _esc(text: str) -> str:
    """Escape LaTeX special characters in a known-plain string."""
    for ch, rep in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                    ("#", r"\#"), ("^", r"\^{}"), ("~", r"\~{}"),
                    ("{", r"\{"), ("}", r"\}"), ("\\", r"\textbackslash{}")]:
        text = text.replace(ch, rep)
    return text


_LATEX_CMD_RE = re.compile(r"(\\[a-zA-Z]+\{[^}]*\}|\\[a-zA-Z]+\{\}|\\[^ ])")

def _esc_plain(text: str) -> str:
    """Escape special chars only in the plain-text runs, leaving LaTeX commands intact."""
    parts = _LATEX_CMD_RE.split(text)
    result = []
    for j, part in enumerate(parts):
        if _LATEX_CMD_RE.match(part):
            result.append(part)
        else:
            for ch, rep in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#")]:
                part = part.replace(ch, rep)
            result.append(part)
    return "".join(result)
