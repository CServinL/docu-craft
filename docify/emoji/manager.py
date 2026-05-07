from pathlib import Path
from ..storage import registry

_SUBDIR = "emoji-sets"


class EmojiManager:
    @staticmethod
    def set_dir(name: str) -> Path:
        path = registry.find_asset(_SUBDIR, name)
        if path is None:
            available = EmojiManager.list()
            raise FileNotFoundError(
                f"Emoji set '{name}' not found.\n"
                f"  Available : {available or ['(none)']}\n"
                f"  Stores    : {[str(s) for s in registry.all()]}\n"
                f"  Download  : python -m docify.emoji.downloader twemoji"
            )
        return path

    @staticmethod
    def list() -> list[str]:
        seen: dict[str, None] = {}
        for d in registry.search(_SUBDIR):
            for item in sorted(d.iterdir()):
                if item.is_dir() and item.name not in seen:
                    seen[item.name] = None
        return list(seen)
