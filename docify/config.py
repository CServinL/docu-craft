from pathlib import Path
import yaml

DOCIFY_HOME        = Path.home() / "docify"
USER_THEMES_DIR    = DOCIFY_HOME / "themes"
USER_SKELETONS_DIR = DOCIFY_HOME / "skeletons"
USER_CONFIG_FILE   = DOCIFY_HOME / "config.yaml"

_HARDCODED_DEFAULTS: dict = {
    "format": "pdf",
    "engine": None,
    "theme":  "scholar",
}


def ensure_home() -> None:
    for d in [USER_THEMES_DIR, USER_SKELETONS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_settings(project_dir: Path | None = None) -> dict:
    """Return merged settings following the resolution chain:
    hardcoded defaults → user config → project config.
    Document frontmatter and explicit render() args are applied on top by Document.
    """
    settings = dict(_HARDCODED_DEFAULTS)

    # 1. User-level: ~/docify/config.yaml
    if USER_CONFIG_FILE.exists():
        data = yaml.safe_load(USER_CONFIG_FILE.read_text(encoding="utf-8")) or {}
        settings.update(data.get("defaults", {}))

    # 2. Project-level: .docify.yaml next to the document (or any parent up to root)
    if project_dir:
        for candidate in [project_dir, *project_dir.parents]:
            for name in (".docify.yaml", "docify.yaml"):
                path = candidate / name
                if path.exists():
                    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                    settings.update(data.get("defaults", {}))
                    return settings   # stop at the first file found

    return settings
