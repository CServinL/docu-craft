from pathlib import Path
from .base import Theme
from ..config import USER_THEMES_DIR, ensure_home

_BUILTIN_DIR = Path(__file__).parent / "builtin"


class ThemeManager:
    @staticmethod
    def load(name: str) -> Theme:
        ensure_home()
        for search_dir in [USER_THEMES_DIR, _BUILTIN_DIR]:
            theme_dir = search_dir / name
            if theme_dir.is_dir():
                return Theme.from_dir(theme_dir)
        raise FileNotFoundError(
            f"Theme '{name}' not found.\n"
            f"  Built-in: {_BUILTIN_DIR}\n"
            f"  User:     {USER_THEMES_DIR}"
        )

    @staticmethod
    def list() -> list[str]:
        ensure_home()
        names: set[str] = set()
        for search_dir in [USER_THEMES_DIR, _BUILTIN_DIR]:
            if search_dir.is_dir():
                names.update(d.name for d in search_dir.iterdir() if d.is_dir())
        return sorted(names)
