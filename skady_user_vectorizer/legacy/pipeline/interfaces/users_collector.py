from global_types import User
from abc import ABC, abstractmethod


class UsersCollector(ABC):
    @abstractmethod
    def run(self, start_user: User, need_to_obtain: int = 1000, nb_processed_friends: int = 10):
        ...
