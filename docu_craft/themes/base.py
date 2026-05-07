from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class Theme:
    name: str
    css: str
    latex_preamble: str = ""
    latex_doc_class: str = "12pt,a4paper"
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dir(cls, theme_dir: Path) -> "Theme":
        css_path      = theme_dir / "style.css"
        meta_path     = theme_dir / "theme.yaml"
        preamble_path = theme_dir / "latex" / "preamble.tex"

        css  = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        preamble  = preamble_path.read_text(encoding="utf-8") if preamble_path.exists() else ""
        doc_class = meta.get("latex", {}).get("doc_class", "12pt,a4paper")

        return cls(
            name=theme_dir.name,
            css=css,
            latex_preamble=preamble,
            latex_doc_class=doc_class,
            meta=meta,
        )
