from abc import ABC, abstractmethod
from global_types import Users
from typing import List


class InfoRetriever(ABC):
    @abstractmethod
    def get_friends(self, users: Users, max_friends: int) -> Users:
        ...

    @abstractmethod
    def check_groups_open(self, users: Users) -> List[bool]:
        ...

    @abstractmethod
    def check_friends_open(self, users: Users) -> List[bool]:
        ...
