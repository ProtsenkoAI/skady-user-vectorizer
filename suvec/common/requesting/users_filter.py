from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np

from suvec.common.top_level_types import User


class UsersFilter(ABC):
    @abstractmethod
    def __call__(self, users: List[User]) -> List[User]:
        ...


class DuplicateUsersFilter(UsersFilter):
    # TODO: at the moment costs too much memory per user because of python objects and set memory usage.
    #   should use numpy arrays/ reduce cost of py objects

    def __init__(self, expansion_size: int = 1000):
        """
        :param expansion_size: the filter uses arrays of fixed shape, so if there's not enough place for users to
            store, concatenates new array of expansion_size
        """
        self.expansion_size = expansion_size
        self.already_added = self._create_new_arr()
        self.last_idx = 0

    def __call__(self, users: List[User]) -> List[User]:
        raw_user_ids = [user.id for user in users]
        uniq_user_ids = list(set(raw_user_ids))

        users_arr = np.array(uniq_user_ids)
        isin_mask = np.isin(users_arr, self.already_added)
        uniq_users_arr = users_arr[~isin_mask]
        uniq_users = [User(user_id) for user_id, isin in zip(uniq_user_ids, isin_mask) if not isin]
        self._add(uniq_users_arr)

        return uniq_users

    def _add(self, usr_ids: np.array):
        users_nb = len(usr_ids)
        need_to_expand_arr_size = self.last_idx + users_nb - len(self.already_added)
        if need_to_expand_arr_size > 0:
            self.already_added = np.concatenate([self.already_added,
                                                 self._create_new_arr(need_to_expand_arr_size)
                                                 ],
                                                axis=0)

        self.already_added[self.last_idx: self.last_idx + users_nb] = usr_ids
        self.last_idx += users_nb

    def _create_new_arr(self, size: Optional[int] = None):
        if size is None:
            size = self.expansion_size
        return np.empty(size, dtype=np.int32)

    def get_checkpoint(self):
        return list(self.already_added)

    def load_checkpoint(self, checkp_data):
        # Caution: buggy place
        # TODO: possibility of loading checkpoint at the middle of work, not at the start can cause bugs, maybe can
        #   replace with object creator @classmethod all load_checkpoint() functions
        self._add(np.array(checkp_data))
