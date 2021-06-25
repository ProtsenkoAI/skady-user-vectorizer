from abc import ABC, abstractmethod
from ...requesting import Request


class UserUnrelatedErrorListener(ABC):
    @abstractmethod
    def user_unrelated_error(self, request: Request):
        ...
