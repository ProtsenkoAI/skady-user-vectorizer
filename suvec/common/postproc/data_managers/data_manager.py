from abc import ABC, abstractmethod
from typing import List, Tuple

from suvec.common.top_level_types import User, Group


UserData = dict
UsersData = List[Tuple[int, UserData]]


class DataManager(ABC):

    @abstractmethod
    def save_user_friends(self, user: User, friends: List[User]):
        ...

    @abstractmethod
    def save_user_groups(self, user: User, groups: List[Group]):
        ...

    def delete_user(self, user_id: str):
        ...
