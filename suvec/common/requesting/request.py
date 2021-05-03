from abc import ABC, abstractmethod

from common.top_level_types import User
from ..executing import Response


class Request(ABC):
    def __init__(self, user: User, responses_factory):  # TODO: add factory typing
        self.user = user
        self.responses_factory = responses_factory

    @abstractmethod
    def get_method(self) -> str:
        ...

    def get_request_kwargs(self) -> dict:
        return {"user_id": self.user.id}

    @abstractmethod
    def create_response(self, resp_raw) -> Response:  # TODO: add typing
        ...
