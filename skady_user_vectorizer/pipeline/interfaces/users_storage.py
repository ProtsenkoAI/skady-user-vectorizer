from abc import ABC, abstractmethod
from global_types import Users


class UsersStorage(ABC):
    @abstractmethod
    def __len__(self):
        ...

    @abstractmethod
    def extend(self, users: Users):
        ...

    @abstractmethod
    def get_all(self) -> Users:
        ...
