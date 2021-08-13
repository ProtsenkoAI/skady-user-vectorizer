from typing import List, Optional, Dict
from recordclass import recordclass
import logging
import numpy as np

from .data_long_term_saver import DataLongTermSaver
from suvec.common.top_level_types import User, Group
from .data_manager import DataManager, UsersData, UserData

ArrayUserData = recordclass("ArrayUserData", [("friends", Optional[np.array]), ("groups", Optional[np.array])])
ArrayUsersData = Dict[int, ArrayUserData]


class RAMDataManager(DataManager):
    # NOTE: sometimes have mem-leakage issues, because when deleting user data from self.users_data dict,
    #   for some reason gc doesn't free memory

    def __init__(self, long_term_saver: DataLongTermSaver, dmp_long_term_every: int = 2000):
        self.users_data: ArrayUsersData = {}
        self.fully_parsed = []
        self.long_term_saver = long_term_saver
        self.dmp_long_term_every = dmp_long_term_every

    def save_user_friends(self, user: User, friends: List[User]):
        if user.id not in self.users_data:
            self.users_data[user.id] = ArrayUserData(None, None)
        friends_ids = [friend.id for friend in friends]
        self.users_data[user.id].friends = self._to_arr(friends_ids)

        self._user_parsed(user)

    def save_user_groups(self, user: User, groups: List[Group]):
        if user.id not in self.users_data:
            self.users_data[user.id] = ArrayUserData(None, None)
        groups_ids = [group.id for group in groups]
        self.users_data[user.id].groups = self._to_arr(groups_ids)

        self._user_parsed(user)

    def _user_parsed(self, user: User):
        if self._check_fully_parsed(user.id):
            user_data = self.users_data.pop(user.id)
            self.fully_parsed.append((user.id, self._from_arr(user_data)))

        if len(self.fully_parsed) % self.dmp_long_term_every == 0 and len(self.fully_parsed) != 0:
            self.long_term_saver.save(self.fully_parsed)
            self.fully_parsed = []

    def _check_fully_parsed(self, user_id: int):
        user_data = self.users_data[user_id]
        return user_data.friends is not None and user_data.groups is not None

    def get_checkpoint(self) -> UsersData:
        logging.info(f"Number of unpaired users in data_manager checkpoint: {len(self.users_data)}")
        checkp = []
        for user, data in self.users_data.items():
            checkp.append((user, self._from_arr(data)))
        return checkp

    def load_checkpoint(self, checkp_data: UsersData):
        for user, user_data in checkp_data:
            friends, groups = user_data["friends"], user_data["groups"]
            if friends is not None:
                friends = self._to_arr(friends)
            if groups is not None:
                groups = self._to_arr(groups)
            self.users_data[user] = ArrayUserData(friends, groups)

    def _to_arr(self, ids):
        return np.array(ids, dtype=np.int32)

    def _from_arr(self, user_data: ArrayUserData) -> UserData:
        friends = user_data.friends
        groups = user_data.groups
        if friends is not None:
            friends = friends.tolist()
        if groups is not None:
            groups = groups.tolist()

        res = {"friends": friends, "groups": groups}
        return res
