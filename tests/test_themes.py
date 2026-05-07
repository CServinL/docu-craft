import pytest
from docify import ThemeManager
from docify.themes import Theme


class TestThemeManager:
    def test_list_includes_builtins(self):
        themes = ThemeManager.list()
        assert "scholar" in themes
        assert "handout" in themes

    def test_load_scholar(self):
        theme = ThemeManager.load("scholar")
        assert theme.name == "scholar"
        assert len(theme.css) > 0
        assert "Georgia" in theme.css

    def test_load_handout(self):
        theme = ThemeManager.load("handout")
        assert theme.name == "handout"
        assert len(theme.css) > 0

    def test_theme_has_meta(self):
        theme = ThemeManager.load("scholar")
        assert theme.meta.get("name") == "Scholar"

    def test_unknown_theme_raises(self):
        with pytest.raises(FileNotFoundError, match="Theme 'nonexistent' not found"):
            ThemeManager.load("nonexistent")

    def test_user_theme_overrides_builtin(self, tmp_dir):
        from docify.storage import registry, StoreKind
        custom_store = tmp_dir / "mystore"
        scholar_dir  = custom_store / "themes" / "scholar"
        scholar_dir.mkdir(parents=True)
        (scholar_dir / "style.css").write_text("body { color: red; }")
        (scholar_dir / "theme.yaml").write_text("name: Custom Scholar\n")

        store = registry.add(custom_store, kind=StoreKind.EXTENDED, name="test-override")
        try:
            theme = ThemeManager.load("scholar")
            assert theme.css == "body { color: red; }"
        finally:
            registry.remove(custom_store)


class TestTheme:
    def test_from_dir_missing_css_gives_empty_string(self, tmp_dir):
        (tmp_dir / "theme.yaml").write_text("name: Empty\n")
        theme = Theme.from_dir(tmp_dir)
        assert theme.css == ""
        assert theme.meta["name"] == "Empty"

    def test_from_dir_missing_meta_gives_empty_dict(self, tmp_dir):
        (tmp_dir / "style.css").write_text("body {}")
        theme = Theme.from_dir(tmp_dir)
        assert theme.meta == {}
        assert theme.css == "body {}"
