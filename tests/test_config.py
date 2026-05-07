import pytest
from pathlib import Path
from docu_craft.config import load_settings, _HARDCODED_DEFAULTS


class TestLoadSettings:
    def test_hardcoded_defaults_with_no_configs(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", tmp_dir / "nonexistent.yaml")
        result = load_settings(tmp_dir)
        assert result["format"] == _HARDCODED_DEFAULTS["format"]
        assert result["theme"]  == _HARDCODED_DEFAULTS["theme"]
        assert result["engine"] == _HARDCODED_DEFAULTS["engine"]

    def test_user_config_overrides_defaults(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        user_cfg = tmp_dir / "config.yaml"
        user_cfg.write_text("defaults:\n  theme: handout\n  engine: weasyprint\n")
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", user_cfg)
        result = load_settings(tmp_dir / "other")
        assert result["theme"] == "handout"
        assert result["engine"] == "weasyprint"

    def test_project_config_overrides_user_config(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        user_cfg = tmp_dir / "config.yaml"
        user_cfg.write_text("defaults:\n  theme: handout\n  engine: weasyprint\n")
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", user_cfg)

        project_dir = tmp_dir / "project"
        project_dir.mkdir()
        (project_dir / ".docu_craft.yaml").write_text("defaults:\n  engine: reportlab\n")

        result = load_settings(project_dir)
        assert result["engine"] == "reportlab"
        assert result["theme"] == "handout"   # still from user config

    def test_project_config_found_in_parent_dir(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", tmp_dir / "no.yaml")
        (tmp_dir / ".docu_craft.yaml").write_text("defaults:\n  theme: handout\n")
        nested = tmp_dir / "subdir" / "deep"
        nested.mkdir(parents=True)
        result = load_settings(nested)
        assert result["theme"] == "handout"

    def test_docu_craft_yaml_takes_priority_over_dotdocu_craft_yaml(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", tmp_dir / "no.yaml")
        (tmp_dir / ".docu_craft.yaml").write_text("defaults:\n  theme: handout\n")
        (tmp_dir / "docu_craft.yaml").write_text("defaults:\n  theme: scholar\n")
        result = load_settings(tmp_dir)
        # .docu_craft.yaml is checked first
        assert result["theme"] == "handout"

    def test_missing_user_config_does_not_raise(self, tmp_dir, monkeypatch):
        import docu_craft.config as cfg
        monkeypatch.setattr(cfg, "USER_CONFIG_FILE", tmp_dir / "missing.yaml")
        result = load_settings(None)
        assert "format" in result
