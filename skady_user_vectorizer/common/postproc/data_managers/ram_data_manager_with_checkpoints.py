from typing import List
import json

from .ram_data_manager import RAMDataManager
from common.top_level_types import User, Group


class RAMDataManagerWithCheckpoints(RAMDataManager):
    """Wrapper that adds periodic saving of parsed data and ability to load from save
    """
    def __init__(self, save_pth: str, save_every_n_users: int = 100):
        super().__init__()
        self.save_pth = save_pth
        self.fully_saved_users_cnt = 0
        self.last_save_nusers = 0
        self.save_every_n_users = save_every_n_users

    def save_user_friends(self, user: User, friends: List[User]):
        super().save_user_friends(user, friends)
        self._check_user_fully_saved(user)
        self._maybe_save()

    def save_user_groups(self, user: User, groups: List[Group]):
        super().save_user_groups(user, groups)
        self._check_user_fully_saved(user)
        self._maybe_save()

    def _check_user_fully_saved(self, user: User):
        friends_saved = self.get_data()[user.id]["friends"] is not None
        groups_saved = self.get_data()[user.id]["groups"] is not None
        if friends_saved and groups_saved:
            self.fully_saved_users_cnt += 1

    def _maybe_save(self):
        if (self.fully_saved_users_cnt - self.last_save_nusers) >= self.save_every_n_users:
            self.last_save_nusers = self.fully_saved_users_cnt
            self._save()

    def _save(self):
        saved_data = self.get_data()
        with open(self.save_pth, "w") as f:
            json.dump(saved_data, f)

    def load(self):
        with open(self.save_pth) as f:
            data = json.load(f)

        self.set_data(data)
