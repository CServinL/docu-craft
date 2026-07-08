import pytest
from docu_craft.renderers import register, graph
from docu_craft.renderers.base import BaseTransformer
from docu_craft.renderers.pdf_md import (
    _coalesce_split_columns,
    _column_numeric_flags,
    _is_noise_row,
)


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


def _table_pdf(borderless: bool = False) -> bytes:
    """A PDF with a real table, rendered via weasyprint. `borderless=True`
    drops all ruling lines — matching a booktabs-style academic-paper table,
    which PyMuPDF's default "lines" table-finder strategy can't detect at
    all (confirmed empirically: it needs actual gridlines); this project
    uses the "text" strategy instead, which works either way."""
    from weasyprint import HTML
    cell = "padding:4px;"
    hdr = cell if borderless else cell + "border-bottom:1px solid black;"
    html = f"""<html><body>
<h1>Report</h1>
<p>Some intro text about the results.</p>
<table style="border-collapse:collapse; width:100%;">
<tr><th style="{hdr}">Task</th><th style="{hdr}">Chinchilla</th><th style="{hdr}">Gopher</th></tr>
<tr><td style="{cell}">hyperbaton</td><td style="{cell}">54.2</td><td style="{cell}">51.7</td></tr>
<tr><td style="{cell}">winowhy</td><td style="{cell}">62.5</td><td style="{cell}">56.7</td></tr>
<tr><td style="{hdr}">causal_judgment</td><td style="{hdr}">57.4</td><td style="{hdr}">50.8</td></tr>
</table>
<p>Some concluding text.</p>
</body></html>"""
    return HTML(string=html).write_pdf()


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

    # -----------------------------------------------------------------------
    # pdf → md table detection
    # -----------------------------------------------------------------------
    # A flattened table (columns joined into one run-on paragraph, e.g.
    # "hyperbaton 54.2 51.7 winowhy 62.5 56.7 ...") is what a downstream
    # KG-extraction consumer sees as an unbounded enumeration and tries to
    # extract every row as an entity. Rendering the table as real markdown
    # instead gives any consumer a structural signal ("this is a table")
    # instead of just a dense wall of numbers.

    def test_pdf_md_ruled_table_becomes_pipe_table(self):
        t = graph.transformer("pdf", "md")
        result = t.transform(_table_pdf(borderless=False))
        assert "| Task | Chinchilla | Gopher |" in result
        assert "| --- | --- | --- |" in result
        assert "| hyperbaton | 54.2 | 51.7 |" in result

    def test_pdf_md_borderless_table_becomes_pipe_table(self):
        # Default PyMuPDF table-finder strategy needs ruling lines and
        # would miss this entirely — the actual bug this feature fixes.
        t = graph.transformer("pdf", "md")
        result = t.transform(_table_pdf(borderless=True))
        assert "| Task | Chinchilla | Gopher |" in result
        assert "| hyperbaton | 54.2 | 51.7 |" in result

    def test_pdf_md_table_not_also_flattened_as_paragraph(self):
        # The table's own text blocks must not also be emitted as a second,
        # flattened copy alongside the pipe-table rendering.
        t = graph.transformer("pdf", "md")
        result = t.transform(_table_pdf(borderless=True))
        assert "hyperbaton 54.2 51.7" not in result

    def test_pdf_md_table_appears_in_reading_order(self):
        t = graph.transformer("pdf", "md")
        result = t.transform(_table_pdf(borderless=True))
        intro = result.index("Some intro text")
        table = result.index("| Task")
        outro = result.index("Some concluding text")
        assert intro < table < outro

    # -----------------------------------------------------------------------
    # table-detection helper functions
    # -----------------------------------------------------------------------
    # Regression coverage from a real paper (Hoffmann et al. 2022,
    # Chinchilla): PyMuPDF's whitespace-based "text" table strategy
    # over-splits a label cell when its own text has irregular internal
    # spacing (BIG-bench task names like "movie_dialog_same_or_diff"), and
    # separately, false-positives on plain justified prose (variable
    # word-gaps look like column boundaries to a whitespace heuristic).

    def test_column_numeric_flags_identifies_score_columns(self):
        rows = [
            ["hyperbaton", "54.2", "51.7"],
            ["causal judgment", "57.4", "50.8"],
            ["winowhy", "62.5", "56.7"],
        ]
        assert _column_numeric_flags(rows, n_cols=3) == [False, True, True]

    def test_coalesce_split_columns_merges_over_split_label(self):
        # "movie_dialog_same_or_diff" over-split into two label fragments
        numeric_col = [False, False, True, True]
        rows = [
            ["movie", "dialog same or diff", "54.5", "50.7"],
            ["hyperbaton", "", "54.2", "51.7"],
        ]
        result = _coalesce_split_columns(rows, numeric_col)
        assert result == [
            ["movie dialog same or diff", "54.5", "50.7"],
            ["hyperbaton", "54.2", "51.7"],
        ]

    def test_coalesce_split_columns_leaves_all_numeric_table_untouched(self):
        numeric_col = [True, True, True]
        rows = [["1.92e+19", "8.0 Billion", "29968"]]
        assert _coalesce_split_columns(rows, numeric_col) == rows

    def test_coalesce_split_columns_leaves_all_label_table_untouched(self):
        numeric_col = [False, False]
        rows = [["Task", "Chinchilla"]]
        assert _coalesce_split_columns(rows, numeric_col) == rows

    def test_is_noise_row_drops_underscore_only_row(self):
        assert _is_noise_row(["_", "_ _", "", "_"]) is True

    def test_is_noise_row_keeps_real_data_row(self):
        assert _is_noise_row(["hyperbaton", "54.2", "51.7"]) is False

    def test_extract_tables_rejects_table_with_no_numeric_column(self):
        # A false-positive table detection on plain prose has no reliably
        # numeric column at all — confirmed against a real paper page
        # (ethical-considerations prose with short bolded labels) that
        # PyMuPDF's "text" strategy misdetected as a table. Rejecting it
        # lets the block fall back to normal paragraph rendering instead of
        # a garbled pipe-table.
        from docu_craft.renderers.pdf_md import _extract_tables

        class _FakeTable:
            bbox = (0, 0, 100, 100)
            def extract(self):
                return [["Ethical", "Considerations"], ["Data", "described in Rae et al."]]

        class _FakeFinder:
            tables = [_FakeTable()]

        class _FakePage:
            def find_tables(self, **kw):
                return _FakeFinder()

        assert _extract_tables(_FakePage()) == []

    def test_extract_tables_keeps_table_with_a_numeric_column(self):
        from docu_craft.renderers.pdf_md import _extract_tables

        class _FakeTable:
            bbox = (0, 0, 100, 100)
            def extract(self):
                return [["Task", "Score"], ["hyperbaton", "54.2"], ["winowhy", "62.5"]]

        class _FakeFinder:
            tables = [_FakeTable()]

        class _FakePage:
            def find_tables(self, **kw):
                return _FakeFinder()

        results = _extract_tables(_FakePage())
        assert len(results) == 1
        assert "| Task | Score |" in results[0][2]
