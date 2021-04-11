from pipeline.interfaces import UsersStorage
from global_types import Users


class ListUsersStorage(UsersStorage):
    def __init__(self):
        self.users = []

    def extend(self, new_users: Users):
        self.users.extend(new_users)

    def __len__(self):
        return len(self.users)

    def get_all(self):
        return self.users

    def __contains__(self, item):
        return item in self.users
