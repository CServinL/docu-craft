from pathlib import Path
import yaml
from .storage import StorageRegistry, StoreKind, Store, registry

# ── well-known roots ──────────────────────────────────────────────────────────
DOCIFY_HOME   = Path.home() / "docu_craft"
_BUNDLED_ROOT = Path(__file__).parent / "assets"   # docu_craft/assets/ — mirrors ~/docu_craft/

USER_CONFIG_FILE    = DOCIFY_HOME / "config.yaml"
USER_EMOJI_SETS_DIR = DOCIFY_HOME / "emoji-sets"

_HARDCODED_DEFAULTS: dict = {
    "format":    "pdf",
    "engine":    None,
    "theme":     "scholar",
    "emoji_set": None,
}

# ── bootstrap the global registry ────────────────────────────────────────────
# Registered lowest-priority first so that higher-priority stores end up first
# after StorageRegistry.all() sorts by kind priority.

registry.add(_BUNDLED_ROOT, kind=StoreKind.BUNDLED, name="bundled")
registry._stores[-1].readonly = True   # bundled is always read-only

registry.add(DOCIFY_HOME, kind=StoreKind.USER, name="user")


def ensure_home() -> None:
    """Create the user store directories if they don't exist."""
    for sub in ("themes", "skeletons", "emoji-sets"):
        (DOCIFY_HOME / sub).mkdir(parents=True, exist_ok=True)


def add_extended_store(path: str | Path, name: str = "") -> Store:
    """Register an extended store (team folder, mounted drive, etc.)."""
    store = registry.add(path, kind=StoreKind.EXTENDED, name=name or str(path))
    return store


def load_settings(project_dir: Path | None = None) -> dict:
    """Return merged settings following the resolution chain:
    hardcoded defaults → user config → project config.
    Document frontmatter and explicit render() args are applied on top by Document.
    """
    settings = dict(_HARDCODED_DEFAULTS)

    # 1. User-level: ~/docu_craft/config.yaml
    if USER_CONFIG_FILE.exists():
        data = yaml.safe_load(USER_CONFIG_FILE.read_text(encoding="utf-8")) or {}
        settings.update(data.get("defaults", {}))
        # extended stores declared in user config
        for entry in data.get("extended_stores", []):
            path = Path(entry) if isinstance(entry, str) else Path(entry["path"])
            name = entry.get("name", "") if isinstance(entry, dict) else ""
            if path.is_dir() and not any(s.path == path for s in registry.all()):
                add_extended_store(path, name)

    # 2. Project-level: .docu_craft.yaml (walks up from document dir)
    if project_dir:
        for candidate in [project_dir, *project_dir.parents]:
            for fname in (".docu_craft.yaml", "docu_craft.yaml"):
                cfg_path = candidate / fname
                if cfg_path.exists():
                    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
                    settings.update(data.get("defaults", {}))
                    for entry in data.get("extended_stores", []):
                        path = Path(entry) if isinstance(entry, str) else Path(entry["path"])
                        name = entry.get("name", "") if isinstance(entry, dict) else ""
                        if path.is_dir() and not any(s.path == path for s in registry.all()):
                            add_extended_store(path, name)
                    return settings

    return settings
