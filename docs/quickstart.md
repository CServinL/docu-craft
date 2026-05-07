# Quick Start

## Installation

```bash
pip install docu_craft
# with ReportLab support
pip install "docu_craft[reportlab]"
# everything
pip install "docu_craft[all]"
```

## Basic usage

```python
import docu_craft

docu_craft.render("report.md", theme="scholar", format="pdf")
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

Create `.docu_craft.yaml` next to your documents:

```yaml
defaults:
  theme: scholar
  engine: weasyprint
```

## Global defaults

Create `~/docu_craft/config.yaml`:

```yaml
defaults:
  theme: scholar
  format: pdf
```

## Config resolution order

Lowest → highest priority:

1. Hardcoded defaults (`format=pdf`, `theme=scholar`)
2. `~/docu_craft/config.yaml`
3. `.docu_craft.yaml` (walks up from document directory)
4. Document YAML frontmatter
5. Explicit `render()` argument
