"""Render demo.md in all supported formats and emoji modes."""

from pathlib import Path
from docu_craft.document import Document

SRC  = Path(__file__).parent / "demo.md"
OUT  = Path(__file__).parent


def render(label: str, fmt: str, **kwargs):
    doc = Document(SRC)
    doc.apply_theme("scholar")
    out = OUT / f"demo-{label}.{fmt}"
    doc.render(format=fmt, output=out, **kwargs)
    print(f"  {fmt:5}  {out.name}")


print("=== system-emoji (font fallback) ===")
for fmt in ("html", "pdf", "docx", "odt", "latex"):
    render("system-emoji", fmt)

print("=== custom-emoji (twemoji images) ===")
for fmt in ("html", "pdf"):
    render("custom-emoji", fmt, emoji_set="twemoji")
