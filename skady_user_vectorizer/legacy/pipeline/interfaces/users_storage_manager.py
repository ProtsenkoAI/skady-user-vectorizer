from abc import ABC, abstractmethod

from .processed_user_res import UserGroupsRes, UserFriendsRes
from .users_storage import UsersStorage


class UsersStorageManager(ABC):
    def __init__(self, storage: UsersStorage):
        self.storage = storage

    def get_storage(self):
        return self.storage

    def get_all_users(self):
        return self.storage.get_all()

    def get_num_users(self):
        return len(self.storage)

    @abstractmethod
    def save_user_groups(self, user_proc: UserGroupsRes):
        ...

    @abstractmethod
    def save_user_friends(self, user_proc: UserFriendsRes):
        ...
