from typing import List, Any

from interfaces import DataManager, User, Group


class RAMDataManager(DataManager):
    # TODO: refactor
    def __init__(self):
        self.users = []
        self.user_id2data: dict = {}

    def save_user_friends(self, user: User, friends: List[User]):
        self._create_field_if_need(user)
        self._set_field_value(user, "friends", friends)

    def save_user_groups(self, user: User, groups: List[Group]):
        self._create_field_if_need(user)
        self._set_field_value(user, "groups", groups)

    def _create_field_if_need(self, user: User):
        if user.id not in self.user_id2data:
            self.user_id2data[user.id] = {"friends": None, "groups": None}

    def _set_field_value(self, user: User, field_name: str, value: Any):
        self.user_id2data[user.id][field_name] = value

    def filter_already_seen_users(self, users: List[User]) -> List[User]:
        unseen_users = [user for user in users if user not in self.users]
        return unseen_users
