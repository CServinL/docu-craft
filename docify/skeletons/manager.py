from pathlib import Path
from .base import Skeleton
from ..config import USER_SKELETONS_DIR, ensure_home

_BUILTIN_DIR = Path(__file__).parent / "builtin"


class SkeletonManager:
    @staticmethod
    def load(name: str) -> Skeleton:
        ensure_home()
        for search_dir in [USER_SKELETONS_DIR, _BUILTIN_DIR]:
            for ext in [".yaml", ".yml"]:
                path = search_dir / f"{name}{ext}"
                if path.exists():
                    return Skeleton.from_file(path)
        raise FileNotFoundError(f"Skeleton '{name}' not found.")

    @staticmethod
    def list() -> list[str]:
        ensure_home()
        names: set[str] = set()
        for search_dir in [USER_SKELETONS_DIR, _BUILTIN_DIR]:
            if search_dir.is_dir():
                names.update(f.stem for f in search_dir.glob("*.yaml"))
                names.update(f.stem for f in search_dir.glob("*.yml"))
        return sorted(names)
