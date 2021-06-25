from abc import ABC, abstractmethod
from typing import List, Dict

from suvec.common.top_level_types import User, Group


UserData = dict
UsersData = Dict[int, UserData]


class DataManager(ABC):

    @abstractmethod
    def save_user_friends(self, user: User, friends: List[User]):
        ...

    @abstractmethod
    def save_user_groups(self, user: User, groups: List[Group]):
        ...

    @abstractmethod
    def get_data(self) -> UsersData:
        ...

    def delete_user(self, user_id: str):
        ...
