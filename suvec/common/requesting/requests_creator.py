from abc import ABC, abstractmethod
from common.top_level_types import User


class RequestsCreator(ABC):
    @abstractmethod
    def friends_request(self, candidate: User):
        ...

    @abstractmethod
    def groups_request(self, candidate: User):
        ...
