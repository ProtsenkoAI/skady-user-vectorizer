from abc import ABC, abstractmethod
from typing import List

from .request import Request
from common.top_level_types import User


class Requester(ABC):
    @abstractmethod
    def add_users(self, users: List[User]):
        ...

    @abstractmethod
    def get_requests(self) -> List[Request]:
        ...
