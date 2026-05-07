# API Reference

## `docu_craft.Document`

```python
Document(source: str | Path)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `.apply_theme(name)` | `self` | Load and attach a theme |
| `.apply_skeleton(name)` | `self` | Load and attach a skeleton |
| `.validate()` | `self` | Run skeleton validation |
| `.render(format, output, engine, theme)` | `Path` | Render to file |

## `docu_craft.render()`

```python
docu_craft.render(source, theme="scholar", format="pdf", output=None, engine=None) → Path
```

Shorthand for `Document(source).apply_theme(theme).render(...)`.

## `docu_craft.register_renderer()`

```python
docu_craft.register_renderer(format, module_path, engine=None, package=None, install=None)
```

## `docu_craft.register_skeleton()`

```python
docu_craft.register_skeleton(name, module_path)
```

## `docu_craft.ThemeManager`

```python
ThemeManager.load(name: str) → Theme
ThemeManager.list() → list[str]
```

## `docu_craft.SkeletonManager`

```python
SkeletonManager.load(name: str) → Skeleton
SkeletonManager.list() → list[str]
```
