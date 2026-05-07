from pathlib import Path
from ..config import USER_EMOJI_SETS_DIR, ensure_home

_BUILTIN_DIR = Path(__file__).parent / "builtin"


class EmojiManager:
    @staticmethod
    def set_dir(name: str) -> Path:
        ensure_home()
        for search_dir in [USER_EMOJI_SETS_DIR, _BUILTIN_DIR]:
            path = search_dir / name
            if path.is_dir():
                return path
        available = EmojiManager.list()
        raise FileNotFoundError(
            f"Emoji set '{name}' not found.\n"
            f"  Built-in: {_BUILTIN_DIR}\n"
            f"  User:     {USER_EMOJI_SETS_DIR}\n"
            f"  Available: {available or ['(none — run: python -m docify.emoji.downloader twemoji)']}"
        )

    @staticmethod
    def list() -> list[str]:
        ensure_home()
        names: set[str] = set()
        for search_dir in [USER_EMOJI_SETS_DIR, _BUILTIN_DIR]:
            if search_dir.is_dir():
                names.update(d.name for d in search_dir.iterdir() if d.is_dir())
        return sorted(names)
