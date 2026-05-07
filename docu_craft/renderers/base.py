from abc import ABC, abstractmethod
from pathlib import Path


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, document, output: Path, emoji_set: str | None = None) -> Path: ...
