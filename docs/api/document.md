# API Reference

## `docify.Document`

```python
Document(source: str | Path)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `.apply_theme(name)` | `self` | Load and attach a theme |
| `.apply_skeleton(name)` | `self` | Load and attach a skeleton |
| `.validate()` | `self` | Run skeleton validation |
| `.render(format, output, engine, theme)` | `Path` | Render to file |

## `docify.render()`

```python
docify.render(source, theme="scholar", format="pdf", output=None, engine=None) → Path
```

Shorthand for `Document(source).apply_theme(theme).render(...)`.

## `docify.register_renderer()`

```python
docify.register_renderer(format, module_path, engine=None, package=None, install=None)
```

## `docify.register_skeleton()`

```python
docify.register_skeleton(name, module_path)
```

## `docify.ThemeManager`

```python
ThemeManager.load(name: str) → Theme
ThemeManager.list() → list[str]
```

## `docify.SkeletonManager`

```python
SkeletonManager.load(name: str) → Skeleton
SkeletonManager.list() → list[str]
```
