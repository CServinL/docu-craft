from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):
    input_fmt: str
    output_fmt: str

    @abstractmethod
    def transform(self, content: Any, **options) -> Any: ...
