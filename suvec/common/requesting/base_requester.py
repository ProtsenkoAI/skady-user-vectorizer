from typing import List, Callable
from abc import abstractmethod

from ..top_level_types import User
from ..listen_notify import AbstractAccessErrorListener
from .request import Request
from .requests_creator import RequestsCreator
from .requester import Requester


class BaseRequester(Requester):
    def __init__(self, request_creator: RequestsCreator, max_requests_per_call: int = 100):
        self.request_creator = request_creator
        self.max_requests_per_call = max_requests_per_call

    @abstractmethod
    def get_requests(self) -> List[Request]:
        ...

    @abstractmethod
    def add_users(self, users: List[User]):
        ...

    def create_requests(self, users: List[User], request_creator_method: Callable):
        requests = []
        while users:
            requests.append(request_creator_method(users.pop(0)))
        return requests

    def create_friends_requests(self, users: List[User]):
        return [self.request_creator.friends_request(user) for user in users]

    def create_groups_requests(self, users: List[User]):
        return [self.request_creator.groups_request(user) for user in users]
