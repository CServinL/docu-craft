from pathlib import Path

from docu_craft.storage import StoreKind, StorageRegistry, registry


def test_add_store():
    store = registry.add("/path/to/store", kind=StoreKind.EXTENDED, name="test_store")
    assert store.path == Path("/path/to/store")
    assert store.kind == "extended"
    assert store.name == "test_store"


def test_remove_store():
    store = registry.add("/path/to/store", kind=StoreKind.EXTENDED, name="test_store")
    registry.remove("/path/to/store")
    assert not any(s.path == Path("/path/to/store") for s in registry.all())


def test_search(tmp_path):
    themes_dir = tmp_path / "themes"
    themes_dir.mkdir()
    reg = StorageRegistry()
    reg.add(tmp_path, kind=StoreKind.EXTENDED, name="test")
    result = reg.search("themes")
    assert result == [themes_dir]


def test_search_missing_subdir_excluded(tmp_path):
    reg = StorageRegistry()
    reg.add(tmp_path, kind=StoreKind.EXTENDED, name="test")
    result = reg.search("themes")  # themes/ not created
    assert result == []


def test_list_assets(tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "asset1").mkdir()
    (assets_dir / "asset2").mkdir()
    reg = StorageRegistry()
    reg.add(tmp_path, kind=StoreKind.EXTENDED, name="test")
    result = reg.list_assets("assets")
    assert "asset1" in result
    assert "asset2" in result


def test_find_asset(tmp_path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "asset1").mkdir()
    reg = StorageRegistry()
    reg.add(tmp_path, kind=StoreKind.EXTENDED, name="test")
    result = reg.find_asset("assets", "asset1")
    assert result == assets_dir / "asset1"


def test_find_asset_missing_returns_none(tmp_path):
    reg = StorageRegistry()
    reg.add(tmp_path, kind=StoreKind.EXTENDED, name="test")
    assert reg.find_asset("assets", "nonexistent") is None


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
