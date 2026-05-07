import pytest
from pathlib import Path
from docu_craft import Document


class TestFrontmatterParsing:
    def test_no_frontmatter(self, sample_md):
        doc = Document(sample_md)
        assert doc.frontmatter == {}
        assert doc.body.startswith("# My Document")

    def test_frontmatter_parsed(self, sample_md_with_frontmatter):
        doc = Document(sample_md_with_frontmatter)
        assert doc.frontmatter["engine"] == "weasyprint"
        assert doc.frontmatter["theme"] == "scholar"
        assert doc.body.startswith("# Title")

    def test_body_does_not_contain_frontmatter(self, sample_md_with_frontmatter):
        doc = Document(sample_md_with_frontmatter)
        assert "---" not in doc.body
        assert "engine:" not in doc.body

    def test_malformed_frontmatter_treated_as_body(self, tmp_dir):
        md = tmp_dir / "bad.md"
        md.write_text("---\nnot: valid: yaml: [\n---\n\n# Body\n")
        doc = Document(md)
        assert doc.frontmatter == {}


class TestSettingsResolution:
    def test_explicit_arg_wins_over_frontmatter(self, sample_md_with_frontmatter):
        doc = Document(sample_md_with_frontmatter)
        cfg = doc._resolve_settings(format="html", engine="custom", theme="handout")
        assert cfg["format"] == "html"
        assert cfg["engine"] == "custom"
        assert cfg["theme"] == "handout"

    def test_frontmatter_wins_over_project_config(self, sample_md_with_frontmatter, tmp_dir):
        (tmp_dir / ".docu_craft.yaml").write_text("defaults:\n  theme: handout\n  engine: reportlab\n")
        doc = Document(sample_md_with_frontmatter)
        cfg = doc._resolve_settings()   # no explicit args — frontmatter vs project config
        # frontmatter has engine=weasyprint, theme=scholar — beats project config
        assert cfg["engine"] == "weasyprint"
        assert cfg["theme"] == "scholar"

    def test_project_config_wins_over_hardcoded_defaults(self, sample_md, tmp_dir):
        (tmp_dir / ".docu_craft.yaml").write_text("defaults:\n  theme: handout\n")
        doc = Document(sample_md)
        cfg = doc._resolve_settings()
        assert cfg["theme"] == "handout"

    def test_none_explicit_clears_engine(self, sample_md_with_frontmatter):
        doc = Document(sample_md_with_frontmatter)
        cfg = doc._resolve_settings(engine=None)   # explicit None overrides frontmatter
        assert cfg["engine"] is None

    def test_default_output_path(self, sample_md):
        doc = Document(sample_md)
        doc.apply_theme("scholar")
        out = doc.render(format="pdf")
        expected = sample_md.with_suffix(".pdf")
        assert out == expected
        out.unlink()


class TestFluentApi:
    def test_apply_theme_returns_self(self, sample_md):
        doc = Document(sample_md)
        assert doc.apply_theme("scholar") is doc

    def test_apply_skeleton_returns_self(self, sample_md):
        doc = Document(sample_md)
        assert doc.apply_skeleton("academic_article") is doc

    def test_validate_returns_self(self, sample_md):
        doc = Document(sample_md)
        doc.apply_skeleton("academic_article")
        assert doc.validate() is doc
