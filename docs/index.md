# DocuCraft

Convert Markdown into polished documents with reusable themes and skeletons.

## Features

- **Themes** — CSS-based style sets (scholar, handout, tech-doc, official)
- **Skeletons** — document structure templates with required-section validation
- **Renderers** — pluggable output backends (WeasyPrint PDF, ReportLab PDF, LaTeX, HTML, DOCX, Jupyter)
- **Layered config** — defaults → `~/docu_craft/config.yaml` → `.docu_craft.yaml` → frontmatter → explicit args

## Quick start

```python
import docu_craft

# One-liner
docu_craft.render("my_article.md", theme="scholar", format="pdf")

# Fluent API
doc = docu_craft.Document("my_article.md")
doc.apply_theme("scholar") \
   .apply_skeleton("academic_article") \
   .validate() \
   .render(format="pdf")
```

## Navigation

- [Quick Start](quickstart.md)
- [Themes](guides/themes.md)
- [Skeletons](guides/skeletons.md)
- [Renderers](guides/renderers.md)
- [API Reference](api/document.md)
