import importlib
from pathlib import Path
from .base import Skeleton
from ..config import USER_SKELETONS_DIR, ensure_home

_BUILTIN_DIR = Path(__file__).parent / "builtin"

# Registry: name → "module.path:ClassName"
# Populated by register(); YAML file search is the fallback.
_REGISTRY: dict[str, str] = {}


def register(name: str, module_path: str) -> None:
    """Register a skeleton by name.

    module_path must be "dotted.module:ClassName", e.g.:
        "mypackage.skeletons:ThesisSkeleton"
    """
    _REGISTRY[name] = module_path


class SkeletonManager:
    @staticmethod
    def load(name: str) -> Skeleton:
        # 1. explicit registry entry
        if name in _REGISTRY:
            return _load_from_module(_REGISTRY[name])

        # 2. inline "module:Class" syntax
        if ":" in name:
            return _load_from_module(name)

        # 3. YAML file — user dir takes precedence over built-ins
        ensure_home()
        for search_dir in [USER_SKELETONS_DIR, _BUILTIN_DIR]:
            for ext in [".yaml", ".yml"]:
                path = search_dir / f"{name}{ext}"
                if path.exists():
                    return Skeleton.from_file(path)

        raise FileNotFoundError(
            f"Skeleton '{name}' not found.\n"
            f"  Registry: {list(_REGISTRY)}\n"
            f"  User:     {USER_SKELETONS_DIR}\n"
            f"  Built-in: {_BUILTIN_DIR}"
        )

    @staticmethod
    def list() -> list[str]:
        ensure_home()
        names: set[str] = set(_REGISTRY)
        for search_dir in [USER_SKELETONS_DIR, _BUILTIN_DIR]:
            if search_dir.is_dir():
                names.update(f.stem for f in search_dir.glob("*.yaml"))
                names.update(f.stem for f in search_dir.glob("*.yml"))
        return sorted(names)


def _load_from_module(module_path: str) -> Skeleton:
    mod_name, cls_name = module_path.rsplit(":", 1)
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, cls_name)
    return cls()
