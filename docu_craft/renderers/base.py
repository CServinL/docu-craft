from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):
    input_fmt: str
    output_fmt: str
    applies_style: bool = False  # True → theme options (css/preamble) injected by workflow
    priority: int = 10           # lower = preferred when multiple paths exist

    @abstractmethod
    def transform(self, content: Any, **options) -> Any: ...
