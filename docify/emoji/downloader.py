"""Download emoji PNG sets from their official GitHub releases.

Supported sets
--------------
twemoji   — CC-BY 4.0  (Twitter/jdecked) — compatible with Apache 2.0
noto      — Apache 2.0 (Google Fonts)    — same license as Docify

Usage
-----
    python -m docify.emoji.downloader twemoji
    python -m docify.emoji.downloader noto
    python -m docify.emoji.downloader twemoji --size 72
"""

import io
import sys
import zipfile
import tarfile
import argparse
import urllib.request
from pathlib import Path

from ..config import USER_EMOJI_SETS_DIR, ensure_home

# ── set definitions ───────────────────────────────────────────────────────────

_SETS: dict[str, dict] = {
    "twemoji": {
        "url":      "https://github.com/jdecked/twemoji/archive/refs/tags/v15.1.0.zip",
        "license":  "CC-BY 4.0",
        "format":   "zip",
        "sizes":    [72],
        "png_path": lambda size, name: (
            f"twemoji-15.1.0/assets/{size}x{size}/{name}"
            if name.endswith(".png") else None
        ),
        "rename":   lambda name: name,     # already 1f600.png format
    },
    "noto": {
        "url":      "https://github.com/googlefonts/noto-emoji/archive/refs/tags/v2.042.tar.gz",
        "license":  "Apache 2.0",
        "format":   "tar.gz",
        "sizes":    [72],
        "png_path": lambda size, name: (
            f"noto-emoji-2.042/png/{size}/{name}"
            if name.endswith(".png") else None
        ),
        # noto names: emoji_u1f600.png → 1f600.png
        "rename":   lambda name: name.replace("emoji_u", "").replace("_", "-"),
    },
}


# ── downloader ────────────────────────────────────────────────────────────────

def download_set(name: str, size: int = 72, force: bool = False) -> Path:
    if name not in _SETS:
        raise ValueError(f"Unknown emoji set '{name}'. Available: {list(_SETS)}")

    cfg     = _SETS[name]
    out_dir = USER_EMOJI_SETS_DIR / name
    ensure_home()

    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        print(f"'{name}' already downloaded at {out_dir}. Use --force to re-download.")
        return out_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {name} ({cfg['license']}) ...")
    print(f"  Source : {cfg['url']}")
    print(f"  Dest   : {out_dir}")

    data = _fetch(cfg["url"])
    count = _extract(data, cfg, size, out_dir)

    print(f"  Done   : {count} PNGs saved.")
    return out_dir


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        chunks, received = [], 0
        while chunk := resp.read(1 << 16):
            chunks.append(chunk)
            received += len(chunk)
            if total:
                pct = received * 100 // total
                print(f"\r  Downloading ... {pct:3d}%", end="", flush=True)
    print()
    return b"".join(chunks)


def _extract(data: bytes, cfg: dict, size: int, out_dir: Path) -> int:
    count   = 0
    rename  = cfg["rename"]
    matcher = cfg["png_path"]

    if cfg["format"] == "zip":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for entry in zf.namelist():
                fname = Path(entry).name
                if matcher(size, fname) and entry == matcher(size, fname):
                    target = out_dir / rename(fname)
                    target.write_bytes(zf.read(entry))
                    count += 1
    else:  # tar.gz
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            for member in tf.getmembers():
                fname = Path(member.name).name
                expected = matcher(size, fname)
                if expected and member.name == expected:
                    f = tf.extractfile(member)
                    if f:
                        target = out_dir / rename(fname)
                        target.write_bytes(f.read())
                        count += 1

    return count


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Download an emoji PNG set for Docify")
    parser.add_argument("set", choices=list(_SETS), help="Emoji set to download")
    parser.add_argument("--size",  type=int, default=72, help="PNG size in px (default: 72)")
    parser.add_argument("--force", action="store_true",  help="Re-download even if already present")
    args = parser.parse_args()

    out = download_set(args.set, size=args.size, force=args.force)
    print(f"\nSet ready. Use it with:")
    print(f"  doc.render(emoji_set='{args.set}')")
    print(f"  # or in .docify.yaml:")
    print(f"  # defaults:")
    print(f"  #   emoji_set: {args.set}")


if __name__ == "__main__":
    main()
