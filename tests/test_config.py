import os
from pathlib import Path
import yaml
from unittest.mock import patch, mock_open

from docu_craft.config import (
    DOCIFY_HOME,
    USER_CONFIG_FILE,
    _HARDCODED_DEFAULTS,
    ensure_home,
    add_extended_store,
    load_settings,
)

def test_ensure_home():
    with patch('os.makedirs') as makedirs:
        ensure_home()
        makedirs.assert_called_once_with(DOCIFY_HOME, parents=True, exist_ok=True)

def test_add_extended_store():
    path = Path("/path/to/store")
    store = add_extended_store(path)
    assert store.path == path
    assert store.kind == "extended"
    assert store.name == str(path)

@patch('builtins.open', new_callable=mock_open, read_data=yaml.dump({
    "defaults": {"format": "html"},
    "extended_stores": [{"path": "/path/to/extended_store"}]
}))
def test_load_settings_user_config(mock_file):
    settings = load_settings()
    assert settings == {
        **_HARDCODED_DEFAULTS,
        "format": "html"
    }
    mock_file.assert_called_once_with(USER_CONFIG_FILE, 'r', encoding='utf-8')

@patch('builtins.open', new_callable=mock_open, read_data=yaml.dump({
    "defaults": {"format": "latex"}
}))
def test_load_settings_project_config(mock_file):
    project_dir = Path("/path/to/project")
    settings = load_settings(project_dir)
    assert settings == {
        **_HARDCODED_DEFAULTS,
        "format": "latex"
    }
    mock_file.assert_called_once_with(project_dir / ".docu_craft.yaml", 'r', encoding='utf-8')

@patch('builtins.open', new_callable=mock_open, read_data=yaml.dump({
    "defaults": {"format": "html"},
    "extended_stores": [{"path": "/path/to/extended_store"}]
}))
def test_load_settings_with_extended_stores(mock_file):
    settings = load_settings()
    assert settings == {
        **_HARDCODED_DEFAULTS,
        "format": "html"
    }
    mock_file.assert_called_once_with(USER_CONFIG_FILE, 'r', encoding='utf-8')

@patch('builtins.open', new_callable=mock_open, read_data=yaml.dump({
    "defaults": {"format": "latex"}
}))
def test_load_settings_project_config_takes_priority(mock_file):
    project_dir = Path("/path/to/project")
    settings = load_settings(project_dir)
    assert settings == {
        **_HARDCODED_DEFAULTS,
        "format": "latex"
    }
    mock_file.assert_called_once_with(project_dir / ".docu_craft.yaml", 'r', encoding='utf-8')

def test_missing_user_config_does_not_raise():
    result = load_settings(None)
    assert "format" in result
