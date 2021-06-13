from typing import List
import os
from . import utils

from ..listen_notify import RequestSuccessListener
from .base_requester_impl import BaseRequesterImpl
from ..top_level_types import User


class EconomicRequester(BaseRequesterImpl, RequestSuccessListener):
    # TODO: refactor work with files of users
    """When user is added, first schedules one type of request and if it succeeds sends all other.
    Also checks that users are unique"""
    def __init__(self, *args, unused_groups_file_pth, unused_friends_file_pth,
                 max_users_storing: int = 3 * 10 ** 4, save_unused_users_every=10 ** 3,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.already_added = set()

        self.save_unused_users_every = save_unused_users_every
        self.max_users_storing = max_users_storing
        self.unused_groups_users = []
        self.unused_friends_users = []
        self.unused_groups_pth = unused_groups_file_pth
        self.unused_friends_pth = unused_friends_file_pth

    def add_users(self, users: List[User]):
        for user in users:
            if user.id not in self.already_added:
                if len(self.users_to_groups_request) < self.max_users_storing:
                    self.users_to_groups_request.append(user)
                else:
                    self.unused_groups_users.append(user)
                self.already_added.add(user.id)

        self._dump_unused_users(self.unused_groups_users, self.unused_groups_pth)
        self.unused_groups_users = []

    def request_friends_and_groups(self):
        total_requested_users = len(self.users_to_groups_request) + len(self.users_to_friends_request)
        print("AAA total_requested_users", total_requested_users)
        if total_requested_users < self.max_requests_per_call:
            # trying to load needed requests from files
            users_needed = self.max_requests_per_call - total_requested_users
            loaded_groups_request_users = self._try_to_load_users(self.unused_groups_pth, users_needed)
            self.users_to_groups_request += loaded_groups_request_users

            users_needed -= len(loaded_groups_request_users)

            if users_needed > 0:
                loaded_friends_request_users = self._try_to_load_users(self.unused_friends_pth, users_needed)
                self.users_to_friends_request += loaded_friends_request_users

        return super().request_friends_and_groups()

    def request_succeed(self, user: User, req_type: str):
        if req_type == "groups":
            if len(self.users_to_friends_request) < self.max_users_storing:
                self.users_to_friends_request.append(user)
            else:
                self.unused_friends_users.append(user)
                if len(self.unused_friends_users) % self.save_unused_users_every == 0:
                    self._dump_unused_users(self.unused_friends_users, self.unused_friends_pth)
                    self.unused_friends_users = []

    def _dump_unused_users(self, users: List[User], pth: str):
        with open(pth, "a") as f:
            print("AAA dumping", len(users), "unused users")
            for user in users:
                f.write(str(user.id) + "\n")

    def _try_to_load_users(self, pth: str, users_needed: int):
        loaded = []
        if os.path.isfile(pth):
            for _ in range(users_needed):
                last_file_line = utils.get_and_delete_last_file_line(pth)
                if not last_file_line:
                    break
                loaded.append(User(id=int(last_file_line.strip())))
        print("AAA Loaded", len(loaded), "users from a file")
        return loaded
