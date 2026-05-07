import pytest
from docu_craft.renderers import get_renderer, register
from docu_craft.renderers.base import BaseRenderer


class TestRegistry:
    def test_default_pdf_returns_weasyprint(self):
        r = get_renderer("pdf")
        assert type(r).__name__ == "WeasyPrintPDFRenderer"

    def test_explicit_weasyprint_engine(self):
        r = get_renderer("pdf", "weasyprint")
        assert type(r).__name__ == "WeasyPrintPDFRenderer"

    def test_format_case_insensitive(self):
        r = get_renderer("PDF")
        assert type(r).__name__ == "WeasyPrintPDFRenderer"

    def test_engine_case_insensitive(self):
        r = get_renderer("pdf", "WeasyPrint")
        assert type(r).__name__ == "WeasyPrintPDFRenderer"

    def test_unknown_format_raises_value_error(self):
        with pytest.raises(ValueError, match="No renderer registered for format='docx'"):
            get_renderer("docx")

    def test_unknown_engine_raises_value_error(self):
        with pytest.raises(ValueError, match="engine='unknown'"):
            get_renderer("pdf", "unknown")

    def test_missing_dependency_raises_import_error(self):
        register(
            "pdf",
            "docu_craft_fake_pkg.renderer:FakeRenderer",
            engine="_test_missing_dep",
            package="docu_craft-fake-pkg",
            install='pip install "docu_craft-fake-pkg"',
        )
        with pytest.raises(ImportError, match="docu_craft-fake-pkg") as exc_info:
            get_renderer("pdf", "_test_missing_dep")
        assert "pip install" in str(exc_info.value)

    def test_register_custom_renderer(self):
        register("pdf", "tests.fixtures.renderers:DummyRenderer", engine="_dummy")
        r = get_renderer("pdf", "_dummy")
        assert type(r).__name__ == "DummyRenderer"

    def test_renderer_is_base_renderer_subclass(self):
        r = get_renderer("pdf")
        assert isinstance(r, BaseRenderer)
