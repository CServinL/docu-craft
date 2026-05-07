from pathlib import Path
import yaml


class Skeleton:
    """Base class for document skeletons.

    Subclass this in a Python module for custom validation logic.
    For simple section lists, use YAML files instead.
    """

    name: str = ""
    sections: list[dict] = []
    meta: dict = {}

    def validate(self, body: str) -> None:
        missing = [
            s["heading"]
            for s in self.sections
            if s.get("required", False) and s["heading"].lower() not in body.lower()
        ]
        if missing:
            raise ValueError(f"Document is missing required sections: {missing}")

    # ── factory: build from YAML file ────────────────────────────────────────

    @classmethod
    def from_file(cls, path: Path) -> "Skeleton":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        obj = cls()
        obj.name     = path.stem
        obj.sections = data.get("sections", [])
        obj.meta     = data.get("meta", {})
        return obj
