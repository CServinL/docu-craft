from .base import BaseRenderer
from .weasyprint_pdf import WeasyPrintPDFRenderer

# Registry: (format, engine_or_None) → renderer class
# New renderers: add an entry here and create the module under renderers/
_REGISTRY: dict[tuple[str, str | None], type[BaseRenderer]] = {
    ("pdf", None):           WeasyPrintPDFRenderer,
    ("pdf", "weasyprint"):   WeasyPrintPDFRenderer,
}


def get_renderer(format: str, engine: str | None = None) -> BaseRenderer:
    key = (format.lower(), engine.lower() if engine else None)
    cls = _REGISTRY.get(key)
    if cls is None:
        available = [f"format={f!r}, engine={e!r}" for f, e in _REGISTRY]
        raise ValueError(
            f"No renderer for format={format!r}, engine={engine!r}.\n"
            f"Available: {available}"
        )
    return cls()


__all__ = ["get_renderer", "BaseRenderer"]
