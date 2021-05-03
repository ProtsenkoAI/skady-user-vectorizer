from abc import ABC, abstractmethod
from common.top_level_types import User
from .types import RequestResult


class ResponsesFactory(ABC):
    @abstractmethod
    def create_friends_response(self, request_res: RequestResult, user: User):
        ...

    @abstractmethod
    def create_groups_response(self, request_res: RequestResult, user: User):
        ...
