# Docify

Convert Markdown into polished PDFs, LaTeX, and more — with reusable themes, document skeletons, and pluggable renderers.

```python
import docify

docify.render("report.md", theme="scholar", format="pdf")
```

## Installation

```bash
pip install docify

# with ReportLab support
pip install "docify[reportlab]"

# everything
pip install "docify[all]"
```

## Usage

```python
import docify

# one-liner
docify.render("report.md", theme="scholar", format="pdf")

# fluent API
doc = docify.Document("report.md")
doc.apply_theme("scholar") \
   .apply_skeleton("academic_article") \
   .validate() \
   .render(format="pdf")
```

## Themes

Built-in themes: `scholar`, `handout`. Drop custom themes in `~/docify/themes/<name>/style.css`.

## Skeletons

Skeletons define expected document structure and validate required sections.
Built-in: `academic_article`, `plan_trabajo`.

```python
# YAML skeleton
doc.apply_skeleton("academic_article")

# Python module skeleton (custom validation logic)
doc.apply_skeleton("mypackage.skeletons:ThesisSkeleton")
```

## Config

Settings resolve in this order (lowest → highest priority):

1. Hardcoded defaults
2. `~/docify/config.yaml`
3. `.docify.yaml` next to the document
4. YAML frontmatter in the `.md` file
5. Explicit `render()` argument

```yaml
# .docify.yaml
defaults:
  theme: scholar
  engine: weasyprint
```

```markdown
---
theme: handout
engine: weasyprint
---

# My Document
```

## Pluggable renderers

```python
import docify

docify.register_renderer(
    format="pdf",
    module_path="mypackage.renderer:MyRenderer",
    engine="myengine",
    package="mypackage",
    install="pip install mypackage",
)

doc.render(format="pdf", engine="myengine")
```

| Format | Engine | Status |
|--------|--------|--------|
| PDF | weasyprint | ✅ |
| PDF | reportlab | 🚧 WIP |

## License

Apache 2.0 © Christian A. Servin Lozano
