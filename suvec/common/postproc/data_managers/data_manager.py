from abc import ABC, abstractmethod
from typing import List

from .types import UsersData
from suvec.common.top_level_types import User, Group


class DataManager(ABC):
    @abstractmethod
    def save_user_friends(self, user: User, friends: List[User]):
        ...

    @abstractmethod
    def get_data(self) -> UsersData:
        ...

    @abstractmethod
    def save_user_groups(self, user: User, groups: List[Group]):
        ...

    @abstractmethod
    def filter_already_seen_users(self, users: List[User]) -> List[User]:
        ...

    @abstractmethod
    def get_num_users(self):
        ...
