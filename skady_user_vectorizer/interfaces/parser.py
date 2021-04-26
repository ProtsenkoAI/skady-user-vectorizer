from abc import ABC, abstractmethod
from .top_level_types import User


class Parser(ABC):
    @abstractmethod
    def parse(self, response, user: User):
        ...
