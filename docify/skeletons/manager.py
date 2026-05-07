import importlib
from pathlib import Path
from .base import Skeleton
from ..storage import registry

_SUBDIR = "skeletons"

# name → "module:Class" for Python-module skeletons
_REGISTRY: dict[str, str] = {}


def register(name: str, module_path: str) -> None:
    """Register a skeleton by name.

    module_path must be "dotted.module:ClassName".
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

        # 3. YAML file — search all stores in priority order
        for store_dir in registry.search(_SUBDIR):
            for ext in (".yaml", ".yml"):
                path = store_dir / f"{name}{ext}"
                if path.exists():
                    return Skeleton.from_file(path)

        raise FileNotFoundError(
            f"Skeleton '{name}' not found.\n"
            f"  Registry : {list(_REGISTRY)}\n"
            f"  Stores   : {[str(s) for s in registry.all()]}"
        )

    @staticmethod
    def list() -> list[str]:
        names: set[str] = set(_REGISTRY)
        for store_dir in registry.search(_SUBDIR):
            if store_dir.is_dir():
                names.update(f.stem for f in store_dir.glob("*.yaml"))
                names.update(f.stem for f in store_dir.glob("*.yml"))
        return sorted(names)


def _load_from_module(module_path: str) -> Skeleton:
    mod_name, cls_name = module_path.rsplit(":", 1)
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, cls_name)
    return cls()
