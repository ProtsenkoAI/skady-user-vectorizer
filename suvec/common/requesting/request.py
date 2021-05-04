from abc import ABC, abstractmethod
from typing import Any

from suvec.common.top_level_types import User
from suvec.common.executing.responses_factory import ResponsesFactory
from ..executing import Response


class Request(ABC):
    def __init__(self, user: User, responses_factory: ResponsesFactory):
        self.user = user
        self.responses_factory = responses_factory

    @abstractmethod
    def get_method(self) -> str:
        ...

    def get_request_kwargs(self) -> dict:
        return {"user_id": self.user.id}

    @abstractmethod
    def create_response(self, resp_raw: Any) -> Response:
        ...
