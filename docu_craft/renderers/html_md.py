"""HTML → Markdown transformer.

Uses BeautifulSoup4 to extract the article body (strips nav, scripts,
headers, footers, and other page chrome) then html2text to produce clean
Markdown. Requires the [html] optional extra.

SVG handling
------------
If ``svg_dir`` (a Path) is passed, each inline <svg> is extracted to a
numbered .svg file and replaced with a Markdown image reference.
If omitted, SVGs are stripped.

Image handling
--------------
If ``img_dir`` (a Path) is passed, referenced <img> src URLs are downloaded
and saved locally; the src is rewritten to the local path.  Tracking pixels
(1×1 dimensions, data URIs, known ad domains) are skipped and stripped.
Requires ``base_url`` to resolve relative src paths.
"""

import hashlib
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup   # noqa: F401 — triggers ImportError if [html] not installed
import html2text                # noqa: F401

from .base import BaseTransformer

_STRIP_TAGS = [
    "script", "style", "nav", "header", "footer", "aside", "noscript",
    "canvas",
    "d-appendix", "d-bibliography", "d-citation", "d-footnote-list",
]

_ARTICLE_SELECTORS = [
    "d-article",        # Distill pub
    "dt-article",       # older Distill
    "article",
    "[role='main']",
    "main",
    ".content",
    "#content",
    ".post",
    ".entry",
]

_AD_DOMAINS = {
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "amazon-adsystem.com", "facebook.com/tr", "analytics.google.com",
    "bat.bing.com", "px.ads.linkedin.com",
}

_HEADERS = {"User-Agent": "Mozilla/5.0"}


def _is_tracking(src: str, width: str | None, height: str | None) -> bool:
    if src.startswith("data:"):
        return True
    try:
        w, h = int(width or 0), int(height or 0)
        if 0 < w <= 2 and 0 < h <= 2:
            return True
    except (ValueError, TypeError):
        pass
    host = urllib.parse.urlparse(src).netloc
    return any(ad in host for ad in _AD_DOMAINS)


def _extract_svgs(body, svg_dir: Path, stem: str) -> None:
    svg_dir.mkdir(parents=True, exist_ok=True)
    for idx, svg_tag in enumerate(body.find_all("svg"), start=1):
        filename = f"{stem}_fig_{idx:03d}.svg"
        svg_path = svg_dir / filename
        svg_path.write_text(str(svg_tag), encoding="utf-8")
        img = body.new_tag("img", src=str(svg_path), alt=f"Figure {idx}")
        svg_tag.replace_with(img)


def _is_local(src: str) -> bool:
    scheme = urllib.parse.urlparse(src).scheme
    return scheme not in ("http", "https", "ftp") and not src.startswith("data:")


def _download_images(body, img_dir: Path, stem: str, base_url: str) -> None:
    img_dir.mkdir(parents=True, exist_ok=True)
    for img_tag in body.find_all("img"):
        src = img_tag.get("src", "")
        if not src:
            img_tag.decompose()
            continue

        if _is_tracking(src, img_tag.get("width"), img_tag.get("height")):
            img_tag.decompose()
            continue

        # Local relative paths are already correct — leave them alone
        if _is_local(src):
            continue

        abs_src = urllib.parse.urljoin(base_url, src)
        ext = Path(urllib.parse.urlparse(abs_src).path).suffix or ".png"
        name = f"{stem}_img_{hashlib.sha1(abs_src.encode()).hexdigest()[:8]}{ext}"
        local_path = img_dir / name

        if not local_path.exists():
            try:
                req = urllib.request.Request(abs_src, headers=_HEADERS)
                with urllib.request.urlopen(req, timeout=10) as r:
                    local_path.write_bytes(r.read())
            except Exception:
                img_tag.decompose()
                continue

        img_tag["src"] = str(local_path)


class HtmlMdTransformer(BaseTransformer):
    """HTML → Markdown via BeautifulSoup4 + html2text."""

    input_fmt = "html"
    output_fmt = "md"
    applies_style = False
    priority = 1

    def transform(self, content: str, **options) -> str:
        soup = BeautifulSoup(content, "html.parser")

        for tag in soup(_STRIP_TAGS):
            tag.decompose()

        body = None
        for selector in _ARTICLE_SELECTORS:
            body = soup.select_one(selector)
            if body:
                break
        if body is None:
            body = soup.find("body") or soup

        stem = options.get("svg_stem", "doc")

        # SVG extraction
        svg_dir = options.get("svg_dir")
        if svg_dir is not None:
            _extract_svgs(body, Path(svg_dir), stem)
        else:
            for tag in body.find_all("svg"):
                tag.decompose()

        # Image handling:
        # - Local relative paths are always preserved as-is
        # - Remote URLs are downloaded if img_dir + base_url are provided, otherwise stripped
        img_dir  = options.get("img_dir")
        base_url = options.get("base_url", "")
        if img_dir is not None and base_url:
            _download_images(body, Path(img_dir), stem, base_url)
        else:
            for tag in body.find_all("img"):
                src = tag.get("src", "")
                if not src or not _is_local(src):
                    tag.decompose()   # strip remote URLs and empty srcs

        h = html2text.HTML2Text()
        h.ignore_links = options.get("ignore_links", False)
        h.ignore_images = options.get("ignore_images", False)
        h.body_width = options.get("body_width", 0)  # 0 = no line wrapping
        h.protect_links = True
        h.wrap_links = False

        return h.handle(str(body))
