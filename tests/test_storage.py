from pathlib import Path
from unittest.mock import patch, mock_open

from docu_craft.storage import (
    StoreKind,
    StorageRegistry,
    registry,
)

def test_add_store():
    store = registry.add("/path/to/store", kind=StoreKind.EXTENDED, name="test_store")
    assert store.path == Path("/path/to/store")
    assert store.kind == "extended"
    assert store.name == "test_store"

def test_remove_store():
    store = registry.add("/path/to/store", kind=StoreKind.EXTENDED, name="test_store")
    registry.remove("/path/to/store")
    assert not any(s.path == Path("/path/to/store") for s in registry.all())

@patch('os.listdir')
def test_search(mock_listdir):
    mock_listdir.return_value = ["theme1", "theme2"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        themes = registry.search("themes")
        assert themes == [Path("/path/to/store/themes")]

@patch('os.listdir')
def test_list_assets(mock_listdir):
    mock_listdir.return_value = ["asset1", "asset2"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        assets = registry.list_assets("assets")
        assert assets == ["asset1", "asset2"]

@patch('os.listdir')
def test_find_asset(mock_listdir):
    mock_listdir.return_value = ["asset1"]
    with patch('docu_craft.storage.registry.search', return_value=[Path("/path/to/store")]):
        asset = registry.find_asset("assets", "asset1")
        assert asset == Path("/path/to/store/assets/asset1")

def test_store_subdir_helpers():
    s = StorageRegistry()
    store_path = Path("/path/to/store")
    store = s.add(store_path, kind=StoreKind.USER)
    assert store.themes_dir() == store_path / "themes"
    assert store.skeletons_dir() == store_path / "skeletons"
    assert store.emoji_dir() == store_path / "emoji-sets"

def test_bundled_last_in_priority():
    s = StorageRegistry()
    s.add("/path/to/bundled", kind=StoreKind.BUNDLED)
    s.add("/path/to/user", kind=StoreKind.USER)
    s.add("/path/to/extended", kind=StoreKind.EXTENDED)
    order = s.all()
    assert order[0].kind == StoreKind.EXTENDED
    assert order[1].kind == StoreKind.USER
    assert order[2].kind == StoreKind.BUNDLED
