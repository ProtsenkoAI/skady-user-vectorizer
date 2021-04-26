from abc import ABC, abstractmethod

from interfaces import User
from .response import Response


class Request(ABC):
    # TODO: move interface from here
    def __init__(self, user: User, responses_factory):
        self.user = user
        self.responses_factory = responses_factory

    @abstractmethod
    def get_method(self) -> str:
        ...

    def get_request_kwargs(self) -> dict:
        return {"user_id": self.user.id}

    @abstractmethod
    def create_response(self, resp_raw) -> Response:
        ...