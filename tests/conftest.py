import pytest
import shutil
import tempfile
from pathlib import Path


@pytest.fixture
def tmp_dir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)


@pytest.fixture
def sample_md(tmp_dir):
    md = tmp_dir / "sample.md"
    md.write_text(
        "# My Document\n\n"
        "## Introducción\nHello world.\n\n"
        "## Conclusiones\nAll done.\n",
        encoding="utf-8",
    )
    return md


@pytest.fixture
def sample_md_with_frontmatter(tmp_dir):
    md = tmp_dir / "with_frontmatter.md"
    md.write_text(
        "---\n"
        "engine: weasyprint\n"
        "theme: scholar\n"
        "format: pdf\n"
        "---\n\n"
        "# Title\n\nBody text.\n",
        encoding="utf-8",
    )
    return md


@pytest.fixture
def project_config(tmp_dir):
    cfg = tmp_dir / ".docu_craft.yaml"
    cfg.write_text("defaults:\n  engine: weasyprint\n  theme: handout\n")
    return tmp_dir
