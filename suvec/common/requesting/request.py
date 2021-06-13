from abc import ABC, abstractmethod

from suvec.common.top_level_types import User


class Request(ABC):
    def __init__(self, user: User, req_type: str):
        self.user = user
        self.req_type = req_type

    @abstractmethod
    def get_method(self) -> str:
        ...

    def get_type(self):
        return self.req_type

    def get_request_kwargs(self) -> dict:
        return {"user_id": self.user.id}

