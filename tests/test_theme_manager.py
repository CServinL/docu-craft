from pathlib import Path
from unittest.mock import patch, mock_open

from docu_craft.themes.manager import ThemeManager

def test_load():
    with patch('docu_craft.storage.registry.find_asset', return_value=Path("/path/to/theme")):
        theme = ThemeManager.load("scholar")
        assert isinstance(theme, type)

@patch('os.listdir')
def test_list(mock_listdir):
    mock_listdir.return_value = ["theme1", "theme2"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        themes = ThemeManager.list()
        assert themes == ["theme1", "theme2"]
