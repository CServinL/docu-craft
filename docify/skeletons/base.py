from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class Skeleton:
    name: str
    sections: list[dict]
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "Skeleton":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(
            name=path.stem,
            sections=data.get("sections", []),
            meta=data.get("meta", {}),
        )

    def validate(self, body: str) -> None:
        missing = [
            s["heading"]
            for s in self.sections
            if s.get("required", False) and s["heading"].lower() not in body.lower()
        ]
        if missing:
            raise ValueError(f"Document is missing required sections: {missing}")
