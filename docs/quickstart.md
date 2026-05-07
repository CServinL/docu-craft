# Quick Start

## Installation

```bash
pip install docify
# with ReportLab support
pip install "docify[reportlab]"
# everything
pip install "docify[all]"
```

## Basic usage

```python
import docify

docify.render("report.md", theme="scholar", format="pdf")
```

## With frontmatter

Set defaults per-document in YAML frontmatter:

```markdown
---
theme: handout
engine: weasyprint
---

# My Document
...
```

## Project-level config

Create `.docify.yaml` next to your documents:

```yaml
defaults:
  theme: scholar
  engine: weasyprint
```

## Global defaults

Create `~/docify/config.yaml`:

```yaml
defaults:
  theme: scholar
  format: pdf
```

## Config resolution order

Lowest → highest priority:

1. Hardcoded defaults (`format=pdf`, `theme=scholar`)
2. `~/docify/config.yaml`
3. `.docify.yaml` (walks up from document directory)
4. Document YAML frontmatter
5. Explicit `render()` argument
