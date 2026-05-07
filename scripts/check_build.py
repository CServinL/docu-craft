#!/usr/bin/env python3
"""Pre-publish security and quality check for dist/ artifacts."""

import re
import sys
import zipfile
import tarfile
import subprocess
from pathlib import Path

DIST_DIR = Path(__file__).parent.parent / "dist"

CREDENTIAL_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*\S+", "API key"),
    (r"(?i)(secret[_-]?key|secretkey)\s*[:=]\s*\S+", "Secret key"),
    (r"(?i)password\s*[:=]\s*\S+", "Password"),
    (r"(?i)token\s*[:=]\s*[A-Za-z0-9_\-]{20,}", "Token"),
    (r"pypi-[A-Za-z0-9_\-]{40,}", "PyPI token"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub PAT"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private key"),
    (r"(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*\S+", "AWS access key"),
    (r"(?i)\.pypirc", ".pypirc reference"),
]

PROMO_PATTERNS = [
    (r"(?i)co-authored-by:.*anthropic", "Co-Authored-By Anthropic"),
    (r"(?i)co-authored-by:.*claude", "Co-Authored-By Claude"),
    (r"(?i)generated with claude", "Generated-with-Claude promo"),
    (r"(?i)claude\.ai/claude-code", "Claude Code URL promo"),
    (r"(?i)anthropic\.com", "Anthropic URL"),
]

SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot"}

errors = []
warnings = []


def flag(level, filename, match, label):
    msg = f"  [{level}] {filename}: {label!r} — matched: {match.group(0)!r}"
    if level == "ERROR":
        errors.append(msg)
    else:
        warnings.append(msg)


def scan_text(content: str, filename: str):
    for pattern, label in CREDENTIAL_PATTERNS:
        for m in re.finditer(pattern, content):
            flag("ERROR", filename, m, label)
    for pattern, label in PROMO_PATTERNS:
        for m in re.finditer(pattern, content):
            flag("ERROR", filename, m, label)


def scan_member(data: bytes, member_name: str):
    ext = Path(member_name).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return
    scan_text(text, member_name)


def check_wheel(path: Path):
    print(f"Scanning wheel: {path.name}")
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            scan_member(zf.read(name), f"{path.name}/{name}")


def check_sdist(path: Path):
    print(f"Scanning sdist: {path.name}")
    with tarfile.open(path, "r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            f = tf.extractfile(member)
            if f:
                scan_member(f.read(), f"{path.name}/{member.name}")


def check_twine(dist_dir: Path):
    print("Running twine check...")
    result = subprocess.run(
        [sys.executable, "-m", "twine", "check", str(dist_dir / "*")],
        capture_output=True, text=True, shell=False
    )
    # twine check requires shell glob expansion; use a list of files instead
    artifacts = list(dist_dir.rglob("*.whl")) + list(dist_dir.rglob("*.tar.gz"))
    result = subprocess.run(
        [sys.executable, "-m", "twine", "check"] + [str(a) for a in artifacts],
        capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    print(output.strip())
    if result.returncode != 0 or "FAILED" in output:
        errors.append("twine check reported failures — see output above")


def main():
    if not DIST_DIR.exists():
        print(f"No dist/ directory found at {DIST_DIR}")
        sys.exit(1)

    artifacts = list(DIST_DIR.rglob("*.whl")) + list(DIST_DIR.rglob("*.tar.gz"))
    if not artifacts:
        print("No build artifacts found in dist/. Run 'python -m build' first.")
        sys.exit(1)

    for artifact in artifacts:
        if artifact.suffix == ".whl":
            check_wheel(artifact)
        elif artifact.name.endswith(".tar.gz"):
            check_sdist(artifact)

    print()
    check_twine(DIST_DIR)

    print()
    if errors:
        print(f"FAILED — {len(errors)} error(s):")
        for e in errors:
            print(e)
        sys.exit(1)
    if warnings:
        print(f"PASSED with {len(warnings)} warning(s):")
        for w in warnings:
            print(w)
    else:
        print("PASSED — no issues found.")


if __name__ == "__main__":
    main()
