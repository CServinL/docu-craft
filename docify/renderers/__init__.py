import importlib
from .base import BaseRenderer

# Registry: (format, engine_or_None) → "module.path:ClassName"
# Renderers are imported only when first used.
_REGISTRY: dict[tuple[str, str | None], str] = {
    ("pdf", None):         "docify.renderers.weasyprint_pdf:WeasyPrintPDFRenderer",
    ("pdf", "weasyprint"): "docify.renderers.weasyprint_pdf:WeasyPrintPDFRenderer",
}


def register(format: str, module_path: str, engine: str | None = None) -> None:
    """Register a renderer for a (format, engine) pair.

    module_path must be "dotted.module:ClassName", e.g.:
        "mypackage.my_renderer:MyRenderer"
    """
    _REGISTRY[(format.lower(), engine.lower() if engine else None)] = module_path


def get_renderer(format: str, engine: str | None = None) -> BaseRenderer:
    key = (format.lower(), engine.lower() if engine else None)
    path = _REGISTRY.get(key)
    if path is None:
        available = [f"format={f!r} engine={e!r}" for f, e in _REGISTRY]
        raise ValueError(
            f"No renderer for format={format!r}, engine={engine!r}.\n"
            f"Available: {available}"
        )
    mod_name, cls_name = path.rsplit(":", 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)()


__all__ = ["get_renderer", "register", "BaseRenderer"]
