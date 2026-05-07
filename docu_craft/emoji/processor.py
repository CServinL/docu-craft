import base64
from pathlib import Path

try:
    import emoji as _emoji_lib
    _HAS_EMOJI_LIB = True
except ImportError:
    _HAS_EMOJI_LIB = False


def codepoint_filename(char: str) -> str:
    """Return the Noto/Twemoji standard filename for an emoji character.
    Multi-codepoint sequences (ZWJ, flags) are joined with hyphens.
    e.g. 😀 → '1f600.png', 👨‍💻 → '1f468-200d-1f4bb.png'
    """
    return "-".join(f"{ord(c):04x}" for c in char) + ".png"


def _to_data_uri(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def replace_emoji(html: str, set_dir: Path, size_em: float = 1.2) -> str:
    """Replace emoji characters in html with embedded base64 <img> tags.
    Images are inlined as data URIs so the HTML is fully self-contained.
    Falls back to the original character if no PNG is found for it.
    """
    if not _HAS_EMOJI_LIB:
        raise ImportError(
            "Emoji support requires the 'emoji' package.\n"
            "Install it with:  pip install \"docu_craft[emoji]\""
        )
    if not set_dir.is_dir():
        raise FileNotFoundError(
            f"Emoji set directory not found: {set_dir}\n"
            f"Place PNG files there using Noto/Twemoji naming (e.g. 1f600.png for 😀)."
        )

    style = f'height:{size_em}em;vertical-align:middle;display:inline-block;'
    cache: dict[str, str] = {}   # fname → data URI, avoids re-encoding duplicates
    result = []

    for token in _emoji_lib.analyze(html, non_emoji=True):
        char = token.chars
        if isinstance(token.value, _emoji_lib.EmojiMatch):
            fname = codepoint_filename(char)
            img_path = set_dir / fname
            if img_path.exists():
                if fname not in cache:
                    cache[fname] = _to_data_uri(img_path)
                result.append(
                    f'<img src="{cache[fname]}" style="{style}" alt="{char}">'
                )
            else:
                result.append(char)
        else:
            result.append(char)

    return "".join(result)
