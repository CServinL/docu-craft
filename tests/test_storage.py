"""Storage abstraction tests — bundled, user, and extended stores."""

import pytest
from pathlib import Path
from docu_craft.storage import StorageRegistry, Store, StoreKind


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fresh_registry():
    """A clean registry with no stores — isolated from the global one."""
    return StorageRegistry()


@pytest.fixture
def populated_registry(tmp_dir):
    """Registry with one store of each kind, each containing a 'themes' subdir."""
    reg = StorageRegistry()
    for kind, name in [
        (StoreKind.BUNDLED,  "bundled"),
        (StoreKind.USER,     "user"),
        (StoreKind.EXTENDED, "extended"),
    ]:
        root = tmp_dir / name
        (root / "themes" / "mytheme").mkdir(parents=True)
        (root / "themes" / "mytheme" / "style.css").write_text(f"/* {name} */")
        s = reg.add(root, kind=kind, name=name)
        if kind == StoreKind.BUNDLED:
            s.readonly = True
    return reg


# ── bundled store ─────────────────────────────────────────────────────────────

class TestBundledStore:
    def test_bundled_store_is_readonly(self):
        from docu_craft.storage import registry
        bundled = next(s for s in registry.all() if s.kind == StoreKind.BUNDLED)
        assert bundled.readonly is True

    def test_bundled_store_has_themes(self):
        from docu_craft.storage import registry
        dirs = registry.search("themes")
        assert any(d.is_dir() for d in dirs)

    def test_bundled_themes_include_scholar(self):
        from docu_craft.storage import registry
        found = registry.find_asset("themes", "scholar")
        assert found is not None
        assert (found / "style.css").exists()

    def test_bundled_skeletons_include_academic_article(self):
        from docu_craft.storage import registry
        dirs = registry.search("skeletons")
        found = any((d / "academic_article.yaml").exists() for d in dirs)
        assert found

    def test_bundled_emoji_includes_noto_minimal(self):
        from docu_craft.storage import registry
        found = registry.find_asset("emoji-sets", "noto-minimal")
        assert found is not None
        assert any(found.glob("*.png"))

    def test_bundled_store_kind(self):
        from docu_craft.storage import registry
        bundled = next(s for s in registry.all() if s.kind == StoreKind.BUNDLED)
        assert bundled.kind == StoreKind.BUNDLED


# ── user store ────────────────────────────────────────────────────────────────

class TestUserStore:
    def test_user_store_is_not_readonly(self):
        from docu_craft.storage import registry
        user = next(s for s in registry.all() if s.kind == StoreKind.USER)
        assert user.readonly is False

    def test_user_store_kind(self):
        from docu_craft.storage import registry
        user = next(s for s in registry.all() if s.kind == StoreKind.USER)
        assert user.kind == StoreKind.USER

    def test_user_theme_overrides_bundled(self, tmp_dir):
        from docu_craft.storage import registry
        user_root = tmp_dir / "user_override"
        scholar   = user_root / "themes" / "scholar"
        scholar.mkdir(parents=True)
        (scholar / "style.css").write_text("body { color: hotpink; }")
        (scholar / "theme.yaml").write_text("name: Override\n")

        store = registry.add(user_root, kind=StoreKind.USER, name="test-user")
        try:
            from docu_craft import ThemeManager
            theme = ThemeManager.load("scholar")
            assert theme.css == "body { color: hotpink; }"
        finally:
            registry.remove(user_root)

    def test_user_skeleton_overrides_bundled(self, tmp_dir):
        from docu_craft.storage import registry
        user_root  = tmp_dir / "user_skel"
        skel_dir   = user_root / "skeletons"
        skel_dir.mkdir(parents=True)
        (skel_dir / "academic_article.yaml").write_text(
            "sections:\n  - heading: Custom\n    required: true\n"
        )
        store = registry.add(user_root, kind=StoreKind.USER, name="test-user-skel")
        try:
            from docu_craft import SkeletonManager
            s = SkeletonManager.load("academic_article")
            assert s.sections[0]["heading"] == "Custom"
        finally:
            registry.remove(user_root)


# ── extended store ────────────────────────────────────────────────────────────

class TestExtendedStore:
    def test_extended_has_highest_priority(self, populated_registry):
        order = populated_registry.all()
        assert order[0].kind == StoreKind.EXTENDED

    def test_extended_overrides_user_and_bundled(self, populated_registry):
        found = populated_registry.find_asset("themes", "mytheme")
        owning_store = next(
            s for s in populated_registry.all()
            if s.path in found.parents
        )
        assert owning_store.kind == StoreKind.EXTENDED

    def test_add_extended_store(self, tmp_dir):
        from docu_craft import add_extended_store
        from docu_craft.storage import registry
        store_path = tmp_dir / "team_store"
        store_path.mkdir()
        store = add_extended_store(store_path, name="team")
        try:
            assert store.kind == StoreKind.EXTENDED
            assert store in registry.all()
        finally:
            registry.remove(store_path)

    def test_extended_store_removed(self, tmp_dir):
        from docu_craft.storage import registry
        store_path = tmp_dir / "removable"
        store_path.mkdir()
        registry.add(store_path, kind=StoreKind.EXTENDED)
        registry.remove(store_path)
        assert not any(s.path == store_path for s in registry.all())

    def test_multiple_extended_stores_last_added_wins(self, tmp_dir):
        from docu_craft.storage import registry
        for name in ("ext_a", "ext_b"):
            root = tmp_dir / name
            (root / "themes" / "shared").mkdir(parents=True)
            (root / "themes" / "shared" / "style.css").write_text(f"/* {name} */")
            registry.add(root, kind=StoreKind.EXTENDED, name=name)

        found = registry.find_asset("themes", "shared")
        assert found is not None
        # ext_b was added last → highest priority among extended
        assert "ext_b" in str(found)

        registry.remove(tmp_dir / "ext_a")
        registry.remove(tmp_dir / "ext_b")


# ── registry mechanics ────────────────────────────────────────────────────────

class TestRegistryMechanics:
    def test_search_returns_only_existing_dirs(self, fresh_registry, tmp_dir):
        root = tmp_dir / "store"
        (root / "themes").mkdir(parents=True)
        fresh_registry.add(root, kind=StoreKind.USER)
        results = fresh_registry.search("themes")
        assert all(d.is_dir() for d in results)

    def test_find_asset_returns_none_when_missing(self, fresh_registry, tmp_dir):
        root = tmp_dir / "empty"
        root.mkdir()
        fresh_registry.add(root, kind=StoreKind.USER)
        assert fresh_registry.find_asset("themes", "nonexistent") is None

    def test_list_assets_deduplicates_by_name(self, populated_registry):
        names = populated_registry.list_assets("themes")
        assert names.count("mytheme") == 1

    def test_store_subdir_helpers(self, tmp_dir):
        s = Store(path=tmp_dir, kind=StoreKind.USER)
        assert s.themes_dir()    == tmp_dir / "themes"
        assert s.skeletons_dir() == tmp_dir / "skeletons"
        assert s.emoji_dir()     == tmp_dir / "emoji-sets"

    def test_bundled_last_in_priority(self, populated_registry):
        order = populated_registry.all()
        assert order[-1].kind == StoreKind.BUNDLED
