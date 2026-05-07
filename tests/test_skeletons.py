import pytest
from docify import SkeletonManager, register_skeleton
from docify.skeletons import Skeleton


class TestSkeletonManager:
    def test_list_includes_builtins(self):
        names = SkeletonManager.list()
        assert "academic_article" in names
        assert "plan_trabajo" in names

    def test_load_yaml_builtin(self):
        s = SkeletonManager.load("academic_article")
        assert s.name == "academic_article"
        assert len(s.sections) > 0

    def test_load_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError, match="Skeleton 'nope' not found"):
            SkeletonManager.load("nope")

    def test_load_from_inline_module_path(self):
        s = SkeletonManager.load("tests.fixtures.skeletons:SimpleSkeleton")
        assert s.name == "SimpleSkeleton"
        assert len(s.sections) == 2

    def test_register_then_load_by_name(self):
        register_skeleton("myskeleton", "tests.fixtures.skeletons:SimpleSkeleton")
        s = SkeletonManager.load("myskeleton")
        assert s.name == "SimpleSkeleton"

    def test_registered_name_appears_in_list(self):
        register_skeleton("listed_skeleton", "tests.fixtures.skeletons:SimpleSkeleton")
        assert "listed_skeleton" in SkeletonManager.list()

    def test_user_yaml_loaded(self, tmp_dir):
        from docify.storage import registry, StoreKind
        custom_store = tmp_dir / "mystore"
        skeletons_dir = custom_store / "skeletons"
        skeletons_dir.mkdir(parents=True)
        (skeletons_dir / "mythesis.yaml").write_text(
            "sections:\n  - heading: Intro\n    required: true\n"
        )
        registry.add(custom_store, kind=StoreKind.EXTENDED, name="test-skeletons")
        try:
            s = SkeletonManager.load("mythesis")
            assert s.sections[0]["heading"] == "Intro"
        finally:
            registry.remove(custom_store)


class TestSkeletonValidation:
    def test_validate_passes_when_all_required_present(self):
        s = SkeletonManager.load("academic_article")
        body = "## Introducción\nHello\n\n## Conclusiones\nDone"
        s.validate(body)  # should not raise

    def test_validate_fails_on_missing_required(self):
        s = SkeletonManager.load("academic_article")
        with pytest.raises(ValueError, match="missing required sections"):
            s.validate("## Marco Teórico\nOnly this section")

    def test_validate_case_insensitive(self):
        s = SkeletonManager.load("academic_article")
        body = "## INTRODUCCIÓN\nHello\n\n## CONCLUSIONES\nDone"
        s.validate(body)  # should not raise

    def test_custom_validate_override(self):
        class StrictSkeleton(Skeleton):
            sections = [{"heading": "Abstract", "required": True}]

            def validate(self, body: str) -> None:
                super().validate(body)
                if len(body) < 100:
                    raise ValueError("Document is too short")

        s = StrictSkeleton()
        with pytest.raises(ValueError, match="too short"):
            s.validate("## Abstract\nShort.")
