from pathlib import Path
from ..config import USER_EMOJI_SETS_DIR, ensure_home


class EmojiManager:
    @staticmethod
    def set_dir(name: str) -> Path:
        ensure_home()
        path = USER_EMOJI_SETS_DIR / name
        if not path.is_dir():
            available = EmojiManager.list()
            raise FileNotFoundError(
                f"Emoji set '{name}' not found in {USER_EMOJI_SETS_DIR}.\n"
                f"Available: {available or ['(none)']}\n"
                f"Place PNG files in {USER_EMOJI_SETS_DIR / name}/ "
                f"using Noto/Twemoji naming (e.g. 1f600.png for 😀)."
            )
        return path

    @staticmethod
    def list() -> list[str]:
        ensure_home()
        if not USER_EMOJI_SETS_DIR.is_dir():
            return []
        return sorted(d.name for d in USER_EMOJI_SETS_DIR.iterdir() if d.is_dir())
