import pytest
from docu_craft.renderers import register, graph
from docu_craft.renderers.base import BaseTransformer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SIMPLE_HTML = """<!DOCTYPE html>
<html><body>
<article>
  <h1>Test Paper</h1>
  <p>This is a paragraph about transformers.</p>
  <p>Second paragraph with <strong>bold</strong> text.</p>
</article>
</body></html>"""


def _minimal_pdf() -> bytes:
    """Build a tiny valid PDF in memory via weasyprint for testing."""
    from weasyprint import HTML
    return HTML(string="<h1>Test</h1><p>Hello PDF world.</p>").write_pdf()


# ---------------------------------------------------------------------------
# Graph registration
# ---------------------------------------------------------------------------

class TestWorkflowGraph:
    def test_md_html_edge_registered(self):
        assert ("md", "html", None) in graph.edges()

    def test_html_pdf_weasyprint_registered(self):
        assert ("html", "pdf", "weasyprint") in graph.edges()

    def test_html_pdf_default_registered(self):
        assert ("html", "pdf", None) in graph.edges()

    def test_html_md_edge_registered(self):
        assert ("html", "md", None) in graph.edges()

    def test_pdf_md_edge_registered(self):
        assert ("pdf", "md", None) in graph.edges()

    # -----------------------------------------------------------------------
    # Path resolution
    # -----------------------------------------------------------------------

    def test_path_md_to_pdf(self):
        path = graph.path("md", "pdf")
        assert path == [("md", "html"), ("html", "pdf")]

    def test_path_md_to_html(self):
        path = graph.path("md", "html")
        assert path == [("md", "html")]

    def test_path_html_to_md(self):
        path = graph.path("html", "md")
        assert path == [("html", "md")]

    def test_path_pdf_to_md(self):
        path = graph.path("pdf", "md")
        assert path == [("pdf", "md")]

    def test_path_pdf_to_html(self):
        # pdf → md → html  (multi-hop)
        path = graph.path("pdf", "html")
        assert path == [("pdf", "md"), ("md", "html")]

    def test_no_path_raises(self):
        with pytest.raises(Exception):
            graph.path("md", "rtf")

    # -----------------------------------------------------------------------
    # Transformer instantiation
    # -----------------------------------------------------------------------

    def test_transformer_is_base_transformer(self):
        t = graph.transformer("md", "html")
        assert isinstance(t, BaseTransformer)

    def test_transformer_unknown_raises(self):
        with pytest.raises(ValueError, match="No transformer registered"):
            graph.transformer("md", "rtf")

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

    # -----------------------------------------------------------------------
    # md → html transform
    # -----------------------------------------------------------------------

    def test_md_html_transform(self):
        t = graph.transformer("md", "html")
        result = t.transform("# Hello")
        assert "<h1" in result
        assert "Hello" in result

    # -----------------------------------------------------------------------
    # html → md transform
    # -----------------------------------------------------------------------

    def test_html_md_transform_returns_string(self):
        t = graph.transformer("html", "md")
        result = t.transform(_SIMPLE_HTML)
        assert isinstance(result, str)

    def test_html_md_extracts_heading(self):
        t = graph.transformer("html", "md")
        result = t.transform(_SIMPLE_HTML)
        assert "Test Paper" in result

    def test_html_md_extracts_body_text(self):
        t = graph.transformer("html", "md")
        result = t.transform(_SIMPLE_HTML)
        assert "transformers" in result

    def test_html_md_strips_scripts(self):
        html = "<html><body><script>alert(1)</script><p>Keep this.</p></body></html>"
        t = graph.transformer("html", "md")
        result = t.transform(html)
        assert "alert" not in result
        assert "Keep this" in result

    def test_html_md_local_images_preserved(self):
        html = '<html><body><img src="figures/fig_001.png" alt="Figure 1"/><p>Text.</p></body></html>'
        t = graph.transformer("html", "md")
        result = t.transform(html)
        assert "figures/fig_001.png" in result

    def test_html_md_remote_images_stripped_without_img_dir(self):
        html = '<html><body><img src="https://example.com/img.png" alt="x"/><p>Text.</p></body></html>'
        t = graph.transformer("html", "md")
        result = t.transform(html)
        assert "https://example.com/img.png" not in result

    # -----------------------------------------------------------------------
    # pdf → md transform
    # -----------------------------------------------------------------------

    def test_pdf_md_transform_returns_string(self):
        t = graph.transformer("pdf", "md")
        result = t.transform(_minimal_pdf())
        assert isinstance(result, str)

    def test_pdf_md_extracts_text(self):
        t = graph.transformer("pdf", "md")
        result = t.transform(_minimal_pdf())
        assert "Hello PDF world" in result

    def test_pdf_md_extracts_heading(self):
        t = graph.transformer("pdf", "md")
        result = t.transform(_minimal_pdf())
        assert "#" in result   # heading inferred from font size

    def test_pdf_md_image_extraction(self, tmp_path):
        t = graph.transformer("pdf", "md")
        # basic PDF has no images — just verify img_dir option is accepted
        result = t.transform(_minimal_pdf(), img_dir=str(tmp_path), stem="test")
        assert isinstance(result, str)
