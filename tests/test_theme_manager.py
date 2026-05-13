from pathlib import Path
from unittest.mock import patch

from docu_craft.themes.manager import ThemeManager
from docu_craft.themes.base import Theme


def test_load(tmp_path):
    theme_dir = tmp_path / "themes" / "scholar"
    theme_dir.mkdir(parents=True)
    with patch("docu_craft.storage.registry.find_asset", return_value=theme_dir):
        theme = ThemeManager.load("scholar")
    assert isinstance(theme, Theme)


def test_load_not_found_raises():
    with patch("docu_craft.storage.registry.find_asset", return_value=None):
        try:
            ThemeManager.load("nonexistent")
            assert False, "should have raised"
        except FileNotFoundError:
            pass


def test_list(tmp_path):
    themes_dir = tmp_path / "themes"
    (themes_dir / "theme1").mkdir(parents=True)
    (themes_dir / "theme2").mkdir(parents=True)
    with patch("docu_craft.themes.manager.registry.search", return_value=[themes_dir]):
        themes = ThemeManager.list()
    assert "theme1" in themes
    assert "theme2" in themes
