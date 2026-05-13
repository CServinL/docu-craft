"""Render demo.md in all supported formats and conversion directions."""

from pathlib import Path
import urllib.request

from docu_craft.document import Document

SRC  = Path(__file__).parent / "demo.md"
OUT  = Path(__file__).parent


def render(label: str, fmt: str, **kwargs):
    doc = Document(SRC)
    doc.apply_theme("scholar")
    out = OUT / f"demo-{label}.{fmt}"
    doc.render(format=fmt, output=out, **kwargs)
    print(f"  {fmt:5}  {out.name}")


# ---------------------------------------------------------------------------
# md → * (original demo)
# ---------------------------------------------------------------------------

print("=== md → * (system-emoji, font fallback) ===")
for fmt in ("html", "pdf", "docx", "odt", "latex"):
    render("system-emoji", fmt)

print("=== md → * (custom-emoji, twemoji images) ===")
for fmt in ("html", "pdf"):
    render("custom-emoji", fmt, emoji_set="twemoji")


# ---------------------------------------------------------------------------
# html → md
# ---------------------------------------------------------------------------

print("=== html → md ===")
_html = OUT / "demo-input.html"
if not _html.exists():
    # Fetch a small public article as sample input
    try:
        req = urllib.request.Request(
            "https://en.wikipedia.org/wiki/Markdown",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            _html.write_bytes(r.read())
        print(f"  fetched demo-input.html  ({_html.stat().st_size // 1024} KB)")
    except Exception as e:
        print(f"  [skip] could not fetch sample HTML: {e}")

if _html.exists():
    doc = Document(_html)
    out = OUT / "demo-html-to-md.md"
    doc.render(format="md", output=out,
               svg_stem="demo",
               img_dir=OUT / "demo-figures",
               base_url="https://en.wikipedia.org/wiki/Markdown")
    print(f"  md     {out.name}  ({out.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# pdf → md
# ---------------------------------------------------------------------------

print("=== pdf → md ===")
_pdf = OUT / "demo-system-emoji.pdf"   # produced in the first block above
if _pdf.exists():
    doc = Document(_pdf)
    out = OUT / "demo-pdf-to-md.md"
    doc.render(format="md", output=out, stem="demo")
    print(f"  md     {out.name}  ({out.stat().st_size // 1024} KB)")
