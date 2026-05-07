from pathlib import Path
from docu_craft.renderers.base import BaseRenderer


class DummyRenderer(BaseRenderer):
    def render(self, document, output: Path) -> Path:
        output.write_text("dummy output")
        return output
