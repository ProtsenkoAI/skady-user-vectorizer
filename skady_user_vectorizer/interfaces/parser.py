from abc import ABC, abstractmethod
from typing import Optional
from .top_level_types import User


class Parser(ABC):
    @abstractmethod
    def parse_friends(self, response, user: User):
        ...

    @abstractmethod
    def parse_groups(self, response, user: User):
        ...
