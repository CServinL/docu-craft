# Themes

A theme is a folder with a `style.css` and an optional `theme.yaml`.

## Built-in themes

| Name | Description |
|------|-------------|
| `scholar` | Serif fonts, dark navy headings, formal academic style |
| `handout` | Sans-serif, orange accent, for courses and workshops |

## Using a theme

```python
doc.apply_theme("scholar")
# or via render()
doc.render(theme="handout")
```

## Creating a custom theme

```
~/docify/themes/
└── mytheme/
    ├── style.css
    └── theme.yaml   # optional metadata
```

`theme.yaml`:
```yaml
name: My Theme
description: Custom style for my project
```

User themes in `~/docify/themes/` override built-ins of the same name.
