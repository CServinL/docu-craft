# Renderers

docu-craft uses a **weighted DAG** to resolve format conversions. Nodes are format strings (`md`, `html`, `pdf`, `latex`, `docx`, …). Edges are transformer classes. When you request a conversion, Dijkstra finds the lowest-cost path and threads content through each step automatically.

## Built-in renderers

| From | To | Engine | Status | Install |
|------|----|--------|--------|---------|
| `md` | `pdf` | `weasyprint` (default) | ✅ | core |
| `md` | `pdf` | `reportlab` | 🚧 WIP | `pip install "docu-craft[reportlab]"` |
| `md` | `pdf` | `latex` | ✅ | LaTeX install required |
| `md` | `html` | — | ✅ | core |
| `md` | `latex` | — | ✅ | core |
| `md` | `docx` | — | ✅ | `pip install "docu-craft[docx]"` |
| `md` | `odt` | — | ✅ | odfpy |
| `html` | `md` | — | ✅ | `pip install "docu-craft[html]"` |
| `pdf` | `md` | — | ✅ | `pip install "docu-craft[pymupdf]"` |

Multi-hop paths are resolved automatically — `md → pdf` routes through `md → html → pdf`, `pdf → html` routes through `pdf → md → html`, etc.

## Selecting a renderer

```python
# via render() argument
doc.render(format="pdf", engine="weasyprint")
doc.render(format="pdf", engine="latex")

# via frontmatter
# ---
# engine: latex
# ---

# via .docu_craft.yaml
# defaults:
#   engine: weasyprint
```

## HTML → Markdown

Extracts the article body from a web page or local HTML file, strips navigation/scripts/ads, downloads or preserves images, and outputs clean Markdown.

```python
doc = docu_craft.Document("paper.html")
doc.render(format="md",
           svg_stem="paper",
           img_dir="figures/",
           base_url="https://example.com/paper/")
```

Options:

| Option | Default | Effect |
|--------|---------|--------|
| `svg_stem` | `"doc"` | Filename stem for extracted SVG files |
| `svg_dir` | `None` | Save inline SVGs as files here; if None, strips SVGs |
| `img_dir` | `None` | Download remote images here; if None, strips remote imgs |
| `base_url` | `""` | Base URL to resolve relative src attributes |
| `ignore_links` | `False` | Strip hyperlinks from output |
| `ignore_images` | `False` | Strip all images from output |
| `body_width` | `0` | Line wrap width (0 = no wrapping) |

Requires: `pip install "docu-craft[html]"`

## PDF → Markdown

Extracts structured text from a PDF using PyMuPDF. Infers heading levels from font size relative to the dominant body size. Detects tables (via PyMuPDF's text-based table finder, which works even on fully borderless/booktabs-style tables with no ruling lines) and renders them as real `|pipe|table|` markdown instead of flattening rows into run-on prose. Optionally extracts embedded images.

```python
doc = docu_craft.Document("paper.pdf")
doc.render(format="md",
           stem="paper",
           img_dir="figures/",
           page_breaks=False)
```

Options:

| Option | Default | Effect |
|--------|---------|--------|
| `stem` | `"doc"` | Filename stem for extracted image files |
| `img_dir` | `None` | Extract embedded images to this directory |
| `page_breaks` | `False` | Insert `---` between pages |

Heading inference thresholds (font size ratio vs body text):

| Ratio | Heading |
|-------|---------|
| ≥ 1.8× | `#` H1 |
| ≥ 1.4× | `##` H2 |
| ≥ 1.15× | `###` H3 |
| < 1.15× | body paragraph |

Requires: `pip install "docu-craft[pymupdf]"`

## Registering a third-party renderer

```python
import docu_craft

docu_craft.register_transformer(
    from_fmt="html",
    to_fmt="pdf",
    module_path="mypackage.renderer:MyRenderer",
    engine="myengine",
    package="mypackage",
    install="pip install mypackage",
)

doc.render(format="pdf", engine="myengine")
```

## Writing a renderer

```python
from docu_craft.renderers.base import BaseTransformer

class MyTransformer(BaseTransformer):
    input_fmt     = "html"
    output_fmt    = "pdf"
    applies_style = True   # True → theme CSS/preamble injected by workflow
    priority      = 5      # lower = preferred when multiple paths exist

    def transform(self, content: str, **options) -> bytes:
        css = options.get("css", "")
        ...
        return pdf_bytes
```

`applies_style = True` tells the workflow to pass theme options (`css`, `preamble`, `doc_class`, `emoji_set`) to this transformer. Set it `False` for format-conversion steps that don't need styling.
