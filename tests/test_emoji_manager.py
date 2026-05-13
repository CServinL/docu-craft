from pathlib import Path
from unittest.mock import patch

from docu_craft.emoji.manager import EmojiManager


def test_set_dir(tmp_path):
    emoji_dir = tmp_path / "emoji-sets" / "twemoji"
    emoji_dir.mkdir(parents=True)
    with patch("docu_craft.storage.registry.find_asset", return_value=emoji_dir):
        path = EmojiManager.set_dir("twemoji")
    assert path == emoji_dir


def test_set_dir_not_found_raises():
    with patch("docu_craft.storage.registry.find_asset", return_value=None):
        try:
            EmojiManager.set_dir("nonexistent")
            assert False, "should have raised"
        except FileNotFoundError:
            pass


def test_list(tmp_path):
    emoji_dir = tmp_path / "emoji-sets"
    (emoji_dir / "set1").mkdir(parents=True)
    (emoji_dir / "set2").mkdir(parents=True)
    with patch("docu_craft.emoji.manager.registry.search", return_value=[emoji_dir]):
        available_sets = EmojiManager.list()
    assert "set1" in available_sets
    assert "set2" in available_sets
