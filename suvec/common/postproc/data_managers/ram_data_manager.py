from typing import List, Any

from .types import UsersData, UserData
from suvec.common.top_level_types import User, Group
from .data_manager import DataManager


class RAMDataManager(DataManager):
    def __init__(self):
        self.users_data: UsersData = {}

    def get_data(self) -> UsersData:
        return self.users_data

    def set_data(self, data: UsersData):
        self.users_data = data

    def save_user_friends(self, user: User, friends: List[User]):
        self._create_field_if_need(user)
        friends_ids = [friend.id for friend in friends]
        self._set_field_value(user, "friends", friends_ids)

    def save_user_groups(self, user: User, groups: List[Group]):
        self._create_field_if_need(user)
        groups_ids = [group.id for group in groups]
        self._set_field_value(user, "groups", groups_ids)

    def _create_field_if_need(self, user: User):
        if user.id not in self.users_data:
            self.users_data[user.id] = UserData(friends=None, groups=None)

    def _set_field_value(self, user: User, field_name: str, value: Any):
        self.users_data[user.id][field_name] = value

    def filter_already_seen_users(self, users: List[User]) -> List[User]:
        unseen_users = [user for user in users if user not in self.users_data]
        return unseen_users

    def get_num_users(self):
        return len(self.users_data)
