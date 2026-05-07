from pathlib import Path

DOCIFY_HOME       = Path.home() / "docify"
USER_THEMES_DIR   = DOCIFY_HOME / "themes"
USER_SKELETONS_DIR = DOCIFY_HOME / "skeletons"


def ensure_home() -> None:
    for d in [USER_THEMES_DIR, USER_SKELETONS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
