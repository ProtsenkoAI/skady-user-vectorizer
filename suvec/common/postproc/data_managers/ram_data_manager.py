from typing import List, Dict
import logging

from .data_long_term_saver import DataLongTermSaver
from suvec.common.top_level_types import User, Group
from .data_manager import DataManager

UserData = dict
UsersData = Dict[int, UserData]


class RAMDataManager(DataManager):
    def __init__(self, long_term_saver: DataLongTermSaver, dmp_long_term_every: int = 2000):
        self.users_data: UsersData = {}
        self.standard_user_val = lambda: {"friends": None, "groups": None}
        self.cnt_fully_parsed = 0
        self.long_term_saver = long_term_saver
        self.dmp_long_term_every = dmp_long_term_every

    def get_data(self) -> UsersData:
        return self.users_data

    def set_data(self, data: UsersData):
        self.users_data = data

    def save_user_friends(self, user: User, friends: List[User]):
        if user.id not in self.users_data:
            self.users_data[user.id] = self.standard_user_val()
        friends_ids = [friend.id for friend in friends]
        self.users_data[user.id]["friends"] = friends_ids

        self._user_parsed(user)

    def save_user_groups(self, user: User, groups: List[Group]):
        if user.id not in self.users_data:
            self.users_data[user.id] = self.standard_user_val()
        groups_ids = [group.id for group in groups]
        self.users_data[user.id]["groups"] = groups_ids

        self._user_parsed(user)

    def _user_parsed(self, user: User):
        self._maybe_cnt_fully_parsed(user)
        if self.cnt_fully_parsed % self.dmp_long_term_every == 0 and self.cnt_fully_parsed != 0:
            self.dump_long_term()

    def _maybe_cnt_fully_parsed(self, user: User):
        if self._check_fully_parsed(user.id):
            self.cnt_fully_parsed += 1

    def _check_fully_parsed(self, user_id: int):
        user_data = self.users_data[user_id]
        return user_data["friends"] is not None and user_data["groups"] is not None

    def get_num_users(self):
        return len(self.users_data)

    def dump_long_term(self):
        long_term_data = []
        for user, data in self.users_data.items():
            if self._check_fully_parsed(user):
                long_term_data.append((user, data))
                del self.users_data[user]

        self.long_term_saver.save(long_term_data)

    def get_checkpoint(self):
        logging.info(f"Number of unpaired users in data_manager checkpoint: {len(self.users_data)}")
        return self.users_data

    def load_checkpoint(self, checkp_data: dict):
        self.users_data.update(**checkp_data)
