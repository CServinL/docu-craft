---
title: docu-craft Demo
author: Christian A. Servin Lozano
---

# docu-craft

Convert Markdown to polished documents with reusable themes and a DAG workflow engine.

## Features

- **Multiple output formats** — PDF, HTML, LaTeX
- **Pluggable renderers** — WeasyPrint, pdflatex, ReportLab
- **Reusable themes** — CSS for HTML/PDF, LaTeX preambles for print
- **Emoji support** — PNG replacement for PDF output
- **Document skeletons** — validate structure before rendering

## Workflow Engine

The DAG resolves the best path from source to target format automatically.

Default path: `md → html → pdf` (fast, WeasyPrint)

With `engine: latex`: `md → latex → pdf` (high quality, pdflatex)

## Code Example

```python
from docu_craft import render

render("report.md", theme="scholar", format="pdf")
```

Or with the fluent API:

```python
from docu_craft import Document

Document("report.md") \
    .apply_theme("scholar") \
    .apply_skeleton("academic_article") \
    .validate() \
    .render(format="pdf", engine="latex")
```

## Themes

| Theme      | Description                          |
|------------|--------------------------------------|
| scholar    | Academic article, serif fonts        |
| handout    | Course handout, clean layout         |
| tech-doc   | Technical documentation              |
| official   | Formal letter / official document    |

## Storage

Three-tier storage: **bundled** (read-only, ships with the package) →
**user** (`~/docu-craft/`) → **extended** (any mounted filesystem path).
