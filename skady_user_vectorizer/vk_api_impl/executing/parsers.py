from typing import Dict

from common.top_level_types import User, Group
from common.executing import Parser
from common.executing import FriendsParseRes, GroupsParseRes, ResponseObj
ApiResponseResult = Dict


class FriendsParser(Parser):
    def parse(self, response: ResponseObj, user: User) -> FriendsParseRes:
        if response.is_error:
            return FriendsParseRes(user=user, error=response.value)

        user_ids = response.value["items"]
        friends = [User(id=user_id) for user_id in user_ids]
        return FriendsParseRes(user=user, friends=friends)


class GroupsParser(Parser):
    def parse(self, response: ResponseObj, user: User) -> GroupsParseRes:
        if response.is_error:
            return GroupsParseRes(user=user, error=response.value)

        groups_ids = response.value["items"]
        groups = [Group(id=group_id) for group_id in groups_ids]
        return GroupsParseRes(user=user, groups=groups)
