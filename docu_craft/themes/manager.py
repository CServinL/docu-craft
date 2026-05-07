from .base import Theme
from ..storage import registry

_SUBDIR = "themes"


class ThemeManager:
    @staticmethod
    def load(name: str) -> Theme:
        theme_dir = registry.find_asset(_SUBDIR, name)
        if theme_dir is None:
            available = ThemeManager.list()
            stores = [str(s) for s in registry.all()]
            raise FileNotFoundError(
                f"Theme '{name}' not found.\n"
                f"  Available : {available}\n"
                f"  Stores    : {stores}"
            )
        return Theme.from_dir(theme_dir)

    @staticmethod
    def list() -> list[str]:
        seen: dict[str, None] = {}
        for d in registry.search(_SUBDIR):
            for item in sorted(d.iterdir()):
                if item.is_dir() and item.name not in seen:
                    seen[item.name] = None
        return list(seen)
