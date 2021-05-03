from abc import ABC, abstractmethod
from suvec.common.top_level_types import User


class Parser(ABC):
    @abstractmethod
    def parse(self, response, user: User):
        ...
