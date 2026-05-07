import pytest
from docu_craft.renderers import register, graph
from docu_craft.renderers.base import BaseTransformer


class TestWorkflowGraph:
    def test_md_html_edge_registered(self):
        assert ("md", "html", None) in graph.edges()

    def test_html_pdf_weasyprint_registered(self):
        assert ("html", "pdf", "weasyprint") in graph.edges()

    def test_html_pdf_default_registered(self):
        assert ("html", "pdf", None) in graph.edges()

    def test_path_md_to_pdf(self):
        path = graph.path("md", "pdf")
        assert path == [("md", "html"), ("html", "pdf")]

    def test_path_md_to_html(self):
        path = graph.path("md", "html")
        assert path == [("md", "html")]

    def test_no_path_raises(self):
        with pytest.raises(Exception):
            graph.path("md", "docx")

    def test_transformer_is_base_transformer(self):
        t = graph.transformer("md", "html")
        assert isinstance(t, BaseTransformer)

    def test_transformer_unknown_raises(self):
        with pytest.raises(ValueError, match="No transformer registered"):
            graph.transformer("md", "docx")

    def test_missing_dependency_raises_import_error(self):
        register(
            "html", "pdf",
            "docu_craft_fake_pkg.renderer:FakeTransformer",
            engine="_test_missing_dep",
            package="docu_craft-fake-pkg",
            install='pip install "docu_craft-fake-pkg"',
        )
        with pytest.raises(ImportError, match="docu_craft-fake-pkg"):
            graph.transformer("html", "pdf", "_test_missing_dep")

    def test_register_custom_transformer(self):
        register(
            "html", "pdf",
            "tests.fixtures.renderers:DummyTransformer",
            engine="_dummy",
        )
        t = graph.transformer("html", "pdf", "_dummy")
        assert type(t).__name__ == "DummyTransformer"

    def test_md_html_transform(self):
        t = graph.transformer("md", "html")
        result = t.transform("# Hello")
        assert "<h1" in result
        assert "Hello" in result
