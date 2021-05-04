from abc import ABC, abstractmethod

from ...top_level_types import User


class RequestSuccessListener(ABC):
    @abstractmethod
    def request_succeed(self, user: User, req_type: str):
        ...