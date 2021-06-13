from abc import ABC, abstractmethod
from typing import List

from suvec.common.top_level_types import User


class UsersFilter(ABC):
    @abstractmethod
    def __call__(self, users: List[User]) -> List[User]:
        ...


class DuplicateUsersFilter(UsersFilter):
    def __init__(self):
        self.already_added = set()

    def __call__(self, users: List[User]) -> List[User]:
        uniq_users = []
        for user in users:
            if user.id not in self.already_added:
                self.already_added.add(user.id)
                uniq_users.append(user)
        return uniq_users

    def get_checkpoint(self):
        return list(self.already_added)

    def load_checkpoint(self, checkp_data):
        self.already_added.update(checkp_data)


if __name__ == "__main__":
    users_filter = DuplicateUsersFilter()
    print(users_filter([User(123), User(456)]))
    print(users_filter([User(789), User(123)]))
