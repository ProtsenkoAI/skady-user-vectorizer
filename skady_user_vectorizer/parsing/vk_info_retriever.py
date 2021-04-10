from global_types import Users
from typing import List
from pipeline.interfaces import InfoRetriever


class VkInfoRetriever(InfoRetriever):
    def get_friends(self, users: Users, max_friends: int) -> Users:
        raise NotImplementedError

    def check_groups_open(self, users: Users) -> List[bool]:
        raise NotImplementedError

    def check_friends_open(self, users: Users) -> List[bool]:
        raise NotImplementedError
