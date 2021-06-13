from typing import Any
from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def parse(self, response) -> Any:
        ...
