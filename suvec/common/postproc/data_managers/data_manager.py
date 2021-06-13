from abc import ABC, abstractmethod
from typing import List, Dict

from suvec.common.top_level_types import User, Group


class DataManager(ABC):
    UserData = dict
    UsersData = Dict[int, UserData]

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

    @abstractmethod
    def filter_already_seen_users(self, users: List[User]) -> List[User]:
        ...

    @abstractmethod
    def get_num_users(self):
        ...
