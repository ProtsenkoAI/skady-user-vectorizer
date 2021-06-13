from typing import Dict, List

from suvec.common.top_level_types import User, Group
from suvec.common.executing import Parser
ApiResponseResult = Dict


class VkApiFriendsParser(Parser):
    def parse(self, items) -> List[User]:
        friends = [User(id=user_id) for user_id in items]
        return friends


class VkApiGroupsParser(Parser):
    def parse(self, items) -> List[Group]:
        groups = [Group(id=group_id) for group_id in items]
        return groups
