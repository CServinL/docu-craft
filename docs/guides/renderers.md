# Renderers

## Built-in renderers

| Format | Engine | Status | Install |
|--------|--------|--------|---------|
| `pdf` | `weasyprint` (default) | ✅ | `pip install weasyprint` |
| `pdf` | `reportlab` | 🚧 WIP | `pip install "docu_craft[reportlab]"` |

## Selecting a renderer

```python
# via render() argument
doc.render(format="pdf", engine="weasyprint")

# via frontmatter
# ---
# engine: reportlab
# ---

# via .docu_craft.yaml
# defaults:
#   engine: weasyprint
```

## Registering a third-party renderer

```python
import docu_craft

docu_craft.register_renderer(
    format="pdf",
    module_path="mypackage.renderer:MyPDFRenderer",
    engine="myengine",
    package="mypackage",
    install="pip install mypackage",
)

doc.render(format="pdf", engine="myengine")
```

## Writing a renderer

```python
from pathlib import Path
from docu_craft.renderers.base import BaseRenderer

class MyRenderer(BaseRenderer):
    def render(self, document, output: Path) -> Path:
        # document.body     — Markdown source
        # document._theme   — Theme (has .css and .meta)
        # document.frontmatter — dict from YAML header
        output.write_bytes(b"...")
        return output
```
