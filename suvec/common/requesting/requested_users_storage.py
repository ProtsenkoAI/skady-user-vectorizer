from abc import ABC, abstractmethod
from typing import List
import logging
import os
from . import utils

from suvec.common.top_level_types import User


class RequestedUsersStorage(ABC):
    @abstractmethod
    def add_user(self, user: User):
        ...

    @abstractmethod
    def get_users(self, max_nb: int):
        ...


class RequestedUsersFileStorage(RequestedUsersStorage):
    def __init__(self, save_pth, max_users_storing: int = 3 * 10 ** 4, save_unused_users_every=10 ** 3):
        self.save_unused_users_every = save_unused_users_every
        self.max_users_storing = max_users_storing
        self.req_users = []
        self.unused_users = []
        self.save_pth = save_pth

    def add_user(self, user: User):
        if len(self.req_users) < self.max_users_storing:
            self.req_users.append(user)
        else:
            self.unused_users.append(user)

        if len(self.unused_users) == self.save_unused_users_every:
            self._dump_users(self.unused_users)
            self.unused_users = []

    def _dump_users(self, users: List[User]):
        with open(self.save_pth, "a") as f:
            logging.info(f"Dump {len(users)} users to file {self.save_pth}")
            for user in users:
                f.write(str(user.id) + "\n")

    def get_users(self, max_nb: int):
        nb_users_in_ram = len(self.req_users)
        need_to_load = max_nb - nb_users_in_ram
        if need_to_load > 0:
            loaded = self._try_to_load_users(self.save_pth, need_to_load)
            self.req_users.extend(loaded)

        res = self.req_users[:max_nb]
        self.req_users = self.req_users[max_nb:]  # remove returned users
        return res

    @staticmethod
    def _try_to_load_users(pth: str, users_needed: int):
        loaded = []
        if os.path.isfile(pth):
            for _ in range(users_needed):
                last_file_line = utils.get_and_delete_last_file_line(pth)
                if not last_file_line:
                    break
                loaded.append(User(id=int(last_file_line.strip())))
        print("AAA Loaded", len(loaded), "users from a file")
        return loaded

    def get_checkpoint(self):
        return self._get_ids(self.req_users), self._get_ids(self.unused_users)

    def load_checkpoint(self, checkp_data):
        req_users, unused_users = checkp_data
        self.unused_users.extend(self._create_users(unused_users))
        req_users = self._create_users(req_users)
        for user in req_users:
            self.add_user(user)

    def _get_ids(self, users: List[User]):
        return [user.id for user in users]

    def _create_users(self, ids: List[int]):
        return [User(id=user_id) for user_id in ids]
