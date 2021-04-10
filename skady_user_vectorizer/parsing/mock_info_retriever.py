from global_types import Users
from typing import List
from pipeline.interfaces import InfoRetriever


class MockInfoRetriever(InfoRetriever):
    # TODO: passing some config to __init__ is bad practice, have to use creator or something like that
    #   idea: rename this class to creator and generate VkRetriever, etc.
    def __init__(self, config):
        self.config = config

    def get_friends(self, users: Users, max_friends: int) -> Users:
        result = []
        for user in users:
            result += [1, 2, 3]
        return result[:max_friends]

    def check_groups_open(self, users: Users) -> List[bool]:
        result = []
        for user in users:
            if user in [1, 2]:
                result.append(True)
            else:
                result.append(False)
        return result

    def check_friends_open(self, users: Users) -> List[bool]:
        result = []
        for user in users:
            result.append(True)
        return result
