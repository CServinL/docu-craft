from pathlib import Path
import yaml
from unittest.mock import patch

from docu_craft.config import (
    _HARDCODED_DEFAULTS,
    ensure_home,
    add_extended_store,
    load_settings,
)


def test_ensure_home(tmp_path):
    with patch("docu_craft.config.DOCIFY_HOME", tmp_path):
        ensure_home()
    assert (tmp_path / "themes").is_dir()
    assert (tmp_path / "skeletons").is_dir()
    assert (tmp_path / "emoji-sets").is_dir()


def test_add_extended_store():
    path = Path("/path/to/store")
    store = add_extended_store(path)
    assert store.path == path
    assert store.kind == "extended"
    assert store.name == str(path)


def test_load_settings_user_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({"defaults": {"format": "html"}}), encoding="utf-8")
    with patch("docu_craft.config.USER_CONFIG_FILE", cfg):
        settings = load_settings()
    assert settings == {**_HARDCODED_DEFAULTS, "format": "html"}


def test_load_settings_project_config(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".docu_craft.yaml").write_text(
        yaml.dump({"defaults": {"format": "latex"}}), encoding="utf-8"
    )
    with patch("docu_craft.config.USER_CONFIG_FILE", tmp_path / "nonexistent.yaml"):
        settings = load_settings(project_dir)
    assert settings == {**_HARDCODED_DEFAULTS, "format": "latex"}


def test_load_settings_with_extended_stores(tmp_path):
    extended = tmp_path / "extended_store"
    extended.mkdir()
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        yaml.dump({"defaults": {"format": "html"}, "extended_stores": [str(extended)]}),
        encoding="utf-8",
    )
    with patch("docu_craft.config.USER_CONFIG_FILE", cfg):
        settings = load_settings()
    assert settings == {**_HARDCODED_DEFAULTS, "format": "html"}


def test_load_settings_project_config_takes_priority(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".docu_craft.yaml").write_text(
        yaml.dump({"defaults": {"format": "latex"}}), encoding="utf-8"
    )
    user_cfg = tmp_path / "config.yaml"
    user_cfg.write_text(yaml.dump({"defaults": {"format": "html"}}), encoding="utf-8")
    with patch("docu_craft.config.USER_CONFIG_FILE", user_cfg):
        settings = load_settings(project_dir)
    assert settings == {**_HARDCODED_DEFAULTS, "format": "latex"}


def test_missing_user_config_does_not_raise():
    result = load_settings(None)
    assert "format" in result
