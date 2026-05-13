from pathlib import Path
from unittest.mock import patch, mock_open

from docu_craft.emoji.manager import EmojiManager

def test_set_dir():
    with patch('docu_craft.storage.registry.find_asset', return_value=Path("/path/to/emoji-set")):
        path = EmojiManager.set_dir("twemoji")
        assert path == Path("/path/to/emoji-set")

@patch('os.listdir')
def test_list(mock_listdir):
    mock_listdir.return_value = ["set1", "set2"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        available_sets = EmojiManager.list()
        assert available_sets == ["set1", "set2"]

@patch('os.listdir')
def test_find_asset(mock_listdir):
    mock_listdir.return_value = ["asset1"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        asset = EmojiManager.find_asset("assets", "asset1")
        assert asset == Path("/path/to/store/assets/asset1")
