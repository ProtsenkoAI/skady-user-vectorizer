from global_types import User
from .users_storage import UsersStorage
from abc import ABC, abstractmethod


class UsersCollector(ABC):
    @abstractmethod
    def start(self, start_user: User, storage: UsersStorage,
              need_to_obtain: int = 1000, nb_processed_friends: int = 10):
        ...
