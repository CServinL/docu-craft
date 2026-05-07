# Docify

Stop writing PDFs by hand. Write Markdown, get a polished document.

```python
import docify

docify.render("report.md", theme="scholar")
```

---

## What it does

You write content in Markdown. Docify handles everything else:

- **Picks a theme** — fonts, colors, margins, tables, code blocks, all styled consistently
- **Validates structure** — checks that your document has the sections it needs before rendering
- **Handles emoji** — replaces emoji characters with proper PNG images in the PDF
- **Finds your assets** — themes, skeletons, and emoji sets from the package, your home folder, or any mounted path

No more pasting CSS into scripts. No more fighting with PDF libraries. No more `weasyprint.HTML(string=html, base_url='.').write_pdf(...)` every time.

---

## Install

```bash
pip install docify

# with ReportLab support
pip install "docify[reportlab]"

# everything
pip install "docify[all]"
```

---

## Themes

Built-in themes, ready to use:

| Theme | Best for |
|-------|----------|
| `scholar` | Academic articles, PhD documents |
| `handout` | Course materials, workshops |
| `tech-doc` | API docs, technical references |
| `official` | Institutional letters, formal reports |

```python
docify.render("thesis.md", theme="scholar")
docify.render("class_notes.md", theme="handout")
```

Drop your own theme in `~/docify/themes/mytheme/style.css` and use it the same way.

---

## Skeletons

Skeletons define what sections a document should have. Docify tells you if something is missing before you render.

```python
doc = docify.Document("thesis.md")
doc.apply_skeleton("academic_article").validate()  # raises if Introducción or Conclusiones missing
doc.render()
```

Built-in skeletons: `academic_article`, `plan_trabajo`, `tech_doc`, `official_letter`, `course_handout`.

Write your own in YAML or as a Python class with custom validation logic.

---

## Emoji in PDFs

PDF fonts don't render emoji. Docify swaps them for PNG images automatically.

```python
docify.render("notes.md", theme="scholar", emoji_set="twemoji")
```

Two sets ship with the package: `noto-minimal` (60 common emoji, Apache 2.0) and `twemoji` (3800+ emoji, CC-BY 4.0). Download more:

```bash
python -m docify.emoji.downloader twemoji
python -m docify.emoji.downloader noto
```

---

## Config layers

Set defaults once, override whenever you need:

```yaml
# ~/docify/config.yaml — your personal defaults
defaults:
  theme: scholar
  emoji_set: twemoji
```

```yaml
# .docify.yaml — per-project overrides
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
docify.render("file.md", theme="tech-doc")
```

---

## Extended storage

Point Docify at any folder — a team share, a mounted drive, a network path. It searches all of them for themes, skeletons, and emoji sets.

```python
docify.add_extended_store("/mnt/team/docify-assets", name="team")
docify.add_extended_store("G:/Shared/styles", name="gdrive")
```

Or declare it in `.docify.yaml`:

```yaml
extended_stores:
  - /mnt/team/docify-assets
  - path: G:/Shared/styles
    name: gdrive
```

---

## Pluggable renderers

```python
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

---

## License

Apache 2.0 © Christian A. Servin Lozano
