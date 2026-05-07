# Skeletons

A skeleton defines the expected structure of a document and can validate that required sections are present.

## Built-in skeletons

| Name | Required sections |
|------|------------------|
| `academic_article` | Introducción, Conclusiones |
| `plan_trabajo` | Objetivo, Actividades |

## YAML skeleton (simple)

```
~/docify/skeletons/thesis.yaml
```

```yaml
sections:
  - heading: Introducción
    required: true
  - heading: Marco Teórico
    required: false
  - heading: Conclusiones
    required: true
```

## Python module skeleton (custom logic)

```python
from docify.skeletons import Skeleton

class ThesisSkeleton(Skeleton):
    name = "thesis"
    sections = [
        {"heading": "Introducción", "required": True},
        {"heading": "Conclusiones", "required": True},
    ]

    def validate(self, body: str) -> None:
        super().validate(body)
        if "bibliograf" not in body.lower():
            raise ValueError("Thesis must include a bibliography")
```

## Loading skeletons

```python
# by name (YAML file or registered)
doc.apply_skeleton("academic_article")

# inline module path (no registration needed)
doc.apply_skeleton("mypackage.skeletons:ThesisSkeleton")

# register once, use by name
import docify
docify.register_skeleton("thesis", "mypackage.skeletons:ThesisSkeleton")
doc.apply_skeleton("thesis")
```
