# TODO: maybe split the module
from abc import ABC, abstractmethod
# TODO: have dependency from executor internals, have to refactor somehow
from vk_api.requests_pool import RequestResult

from interfaces import User
from .responses import Response, GroupsResponse, FriendsResponse


class Request(ABC):
    def __init__(self, user: User):
        self.user = user

    @abstractmethod
    def get_method(self) -> str:
        ...

    def get_request_kwargs(self) -> dict:
        return {"user_id": self.user.id}

    @abstractmethod
    def create_response(self, resp_raw: RequestResult) -> Response:
        ...


class FriendsRequest(Request):
    def get_method(self) -> str:
        return "friends.get"

    def create_response(self, resp_raw: RequestResult) -> Response:
        return FriendsResponse(resp_raw, user=self.user)


class GroupsRequest(Request):
    def get_method(self) -> str:
        return "groups.get"

    def create_response(self, resp_raw: RequestResult) -> Response:
        return GroupsResponse(resp_raw, user=self.user)
