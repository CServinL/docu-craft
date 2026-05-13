# docu-craft

Stop writing PDFs by hand. Write Markdown, get a polished document.

```python
import docu_craft

docu_craft.render("report.md", theme="scholar")
```

---

## What it does

You write content in Markdown. docu-craft handles everything else:

- **Picks a theme** — fonts, colors, margins, tables, code blocks, all styled consistently across every output format
- **Named document styles** — styles are registered as first-class named styles in DOCX and ODT, visible in Word's Styles pane and LibreOffice's Styles panel, not just inline formatting
- **Multiple output formats** — PDF, HTML, DOCX, ODT, LaTeX from the same source file
- **Handles emoji** — system font fallback or image replacement via downloadable emoji sets
- **Validates structure** — checks that your document has the sections it needs before rendering
- **Finds your assets** — themes, skeletons, and emoji sets from the package, your home folder, or any mounted path

No more pasting CSS into scripts. No more fighting with PDF libraries.

---

## Install

```bash
pip install docu-craft

# with DOCX support
pip install "docu-craft[docx]"

# with HTML → Markdown conversion
pip install "docu-craft[html]"

# with PDF → Markdown extraction
pip install "docu-craft[pymupdf]"

# everything
pip install "docu-craft[all]"
```

---

## Conversion paths

docu-craft uses a weighted DAG to resolve conversions. Ask for any path — it finds the route automatically.

| From | To | Engine | Notes |
|------|----|--------|-------|
| `md` | `pdf` | WeasyPrint (default) | via HTML — full CSS, emoji font support |
| `md` | `pdf` | LaTeX | via pdflatex/xelatex — requires LaTeX install |
| `md` | `html` | — | embedded CSS from theme |
| `md` | `docx` | — | named styles visible in Word's Styles pane |
| `md` | `odt` | — | named styles visible in LibreOffice's Styles panel |
| `md` | `latex` | — | direct Markdown → LaTeX source |
| `html` | `md` | — | extracts article body, strips chrome, preserves images |
| `pdf` | `md` | — | extracts structured text, infers headings from font size |

```python
doc = docu_craft.Document("report.md")
doc.apply_theme("scholar")

doc.render(format="pdf",  output="report.pdf")
doc.render(format="docx", output="report.docx")
doc.render(format="html", output="report.html")

# Convert a web paper to Markdown
doc = docu_craft.Document("paper.html")
doc.render(format="md", output="paper.md", img_dir="figures/", base_url="https://example.com/paper/")

# Extract text from a PDF
doc = docu_craft.Document("paper.pdf")
doc.render(format="md", output="paper.md")
```

---

## Themes

Themes define the full visual identity of a document — fonts, colors, spacing, and every named style — applied consistently across all output formats.

| Theme | Best for |
|-------|----------|
| `scholar` | Academic articles, PhD documents |
| `handout` | Course materials, workshops |
| `tech-doc` | API docs, technical references |
| `official` | Institutional letters, formal reports |

```python
docu_craft.render("thesis.md", theme="scholar")
docu_craft.render("class_notes.md", theme="handout")
```

Drop your own theme in `~/docu_craft/themes/mytheme/` and use it the same way.

### Theme schema

Every theme defines a `styles` block with named semantic styles — `body`, `heading1`–`heading6`, `code_block`, `code_inline`, `table_header`, `table_cell`, `list_item`, `quote`. Each style references a font stack by name (`body`, `header`, or `mono`) and specifies size, color, weight, spacing, and background.

```yaml
# theme.yaml
style:
  fonts:
    body:   ["Georgia", "Times New Roman", "serif"]
    header: ["Arial", "Helvetica", "sans-serif"]
    mono:   ["Courier New", "Courier", "monospace"]
    emoji:  ["Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji"]

  styles:
    heading1:
      font: header
      size: 16
      color: "#1a1a2e"
      bold: true
    code_block:
      font: mono
      size: 9
      background: "#f4f4f4"
```

The same style definitions drive all renderers — Word's "DC Heading 1", LibreOffice's "DC Body Text", and the CSS `h1` rule all come from the same source.

---

## Emoji

### System emoji (font fallback)

By default docu-craft passes emoji through and lets the output application render them using its own font stack. For PDF via WeasyPrint, emoji fonts are resolved automatically:

```yaml
# theme.yaml
style:
  fonts:
    emoji: ["Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Twemoji Mozilla"]
```

docu-craft probes the filesystem for each font (in order: Linux → macOS → Windows) and emits `@font-face` rules pointing to the actual font files. On WSL2, it finds Windows fonts via `/mnt/c/Windows/Fonts/` automatically.

### Custom emoji sets (image replacement)

For consistent, platform-independent emoji across all readers, use an image-based emoji set. Each emoji character is replaced with a PNG from the set.

```python
docu_craft.render("notes.md", theme="scholar", emoji_set="twemoji")
```

Download sets with the built-in downloader:

```bash
python -m docu_craft.emoji.downloader twemoji
python -m docu_craft.emoji.downloader noto
```

#### Twemoji

The recommended custom set. Twemoji (CC-BY 4.0, by Twitter/jdecked) draws every glyph on the same grid at the same size with the same line weights. When you place several emoji side by side they read as a unified visual system — consistent weight, consistent optical size, no surprises. This is the same discipline a monospaced font applies to letterforms. If visual consistency across emoji matters in your documents, Twemoji is the right choice.

Other available sets:

| Set | License | Coverage | Character |
|-----|---------|----------|-----------|
| `twemoji` | CC-BY 4.0 | 3800+ | Grid-locked, uniform, consistent |
| `noto` | Apache 2.0 | 3000+ | Disciplined, clean, Google design system |

---

## Skeletons

Skeletons define what sections a document should have. docu-craft tells you if something is missing before you render.

```python
doc = docu_craft.Document("thesis.md")
doc.apply_skeleton("academic_article").validate()
doc.render()
```

Built-in skeletons: `academic_article`, `plan_trabajo`, `tech_doc`, `official_letter`, `course_handout`.

---

## Config layers

Set defaults once, override whenever you need:

```yaml
# ~/docu_craft/config.yaml — your personal defaults
defaults:
  theme: scholar
  emoji_set: twemoji
```

```yaml
# .docu_craft.yaml — per-project overrides
defaults:
  theme: handout
```

```markdown
---
theme: official
---
# Per-document frontmatter overrides everything above
```

```python
# Explicit argument wins over all of the above
docu_craft.render("file.md", theme="tech-doc")
```

---

## Extended storage

Point docu-craft at any folder — a team share, a mounted drive, a network path. It searches all of them for themes, skeletons, and emoji sets.

```python
docu_craft.add_extended_store("/mnt/team/docu_craft-assets", name="team")
```

```yaml
# .docu_craft.yaml
extended_stores:
  - /mnt/team/docu_craft-assets
  - path: G:/Shared/styles
    name: gdrive
```

---

## Pluggable renderers

```python
docu_craft.register_renderer(
    format="pdf",
    module_path="mypackage.renderer:MyRenderer",
    engine="myengine",
    package="mypackage",
    install="pip install mypackage",
)

doc.render(format="pdf", engine="myengine")
```

The renderer graph is a weighted DAG — preference between equivalent paths (e.g. `md→html→pdf` vs `md→latex→pdf`) is configured per project via the `engine` setting.

---

## License

Apache 2.0 © Christian A. Servin Lozano
