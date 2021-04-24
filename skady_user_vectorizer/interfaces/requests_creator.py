from abc import ABC, abstractmethod
from typing import Callable
from .top_level_types import User


class RequestsCreator(ABC):
    # TODO: add return typings
    @abstractmethod
    def friends_request(self, candidate: User, callback: Callable):
        ...

    @abstractmethod
    def groups_request(self, candidate: User, callback: Callable):
        ...

    @abstractmethod
    def auth_request(self, callback: Callable):
        ...

    @abstractmethod
    def change_proxy(self):
        ...
