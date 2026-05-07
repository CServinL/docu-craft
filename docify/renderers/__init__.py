import importlib
from .base import BaseRenderer

# Registry: (format, engine_or_None) → entry dict
# "path"    — "module:ClassName" imported lazily on first use
# "package" — PyPI package name, for the error message
# "install" — pip install command shown to the user on ImportError
_REGISTRY: dict[tuple[str, str | None], dict] = {
    ("pdf", None): {
        "path":    "docify.renderers.weasyprint_pdf:WeasyPrintPDFRenderer",
        "package": "weasyprint",
        "install": "pip install weasyprint",
    },
    ("pdf", "weasyprint"): {
        "path":    "docify.renderers.weasyprint_pdf:WeasyPrintPDFRenderer",
        "package": "weasyprint",
        "install": "pip install weasyprint",
    },
}


def register(
    format: str,
    module_path: str,
    engine: str | None = None,
    package: str | None = None,
    install: str | None = None,
) -> None:
    """Register a renderer for a (format, engine) pair.

    module_path  — "dotted.module:ClassName"
    package      — PyPI name shown in missing-dependency errors
    install      — full pip command shown to the user (defaults to 'pip install <package>')
    """
    pkg = package or module_path.split(".")[0]
    _REGISTRY[(format.lower(), engine.lower() if engine else None)] = {
        "path":    module_path,
        "package": pkg,
        "install": install or f"pip install {pkg}",
    }


def get_renderer(format: str, engine: str | None = None) -> BaseRenderer:
    key = (format.lower(), engine.lower() if engine else None)
    entry = _REGISTRY.get(key)

    if entry is None:
        available = [
            f"format={f!r}" + (f" engine={e!r}" if e else "")
            for f, e in _REGISTRY
        ]
        raise ValueError(
            f"No renderer registered for format={format!r}"
            + (f", engine={engine!r}" if engine else "")
            + f".\nAvailable: {available}"
        )

    mod_name, cls_name = entry["path"].rsplit(":", 1)
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        raise ImportError(
            f"Renderer '{entry['path']}' requires '{entry['package']}' which is not installed.\n"
            f"Install it with:  {entry['install']}"
        ) from None

    return getattr(mod, cls_name)()


__all__ = ["get_renderer", "register", "BaseRenderer"]
