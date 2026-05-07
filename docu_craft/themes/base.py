from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class Theme:
    name: str
    css: str
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dir(cls, theme_dir: Path) -> "Theme":
        css_path  = theme_dir / "style.css"
        meta_path = theme_dir / "theme.yaml"
        css  = css_path.read_text(encoding="utf-8")  if css_path.exists()  else ""
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        return cls(name=theme_dir.name, css=css, meta=meta)
