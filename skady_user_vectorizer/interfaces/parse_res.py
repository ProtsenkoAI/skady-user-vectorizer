from typing import List

from .parse_statuses import UnknownStatus, AccessErrorStatus, SuccessParseStatus, ParseStatus
from .top_level_types import User, Group


class ParseRes:
    def __init__(self, user: User, success: bool, access_error: bool):
        self.user = user
        if access_error:
            self.status = AccessErrorStatus
        elif success:
            self.status = SuccessParseStatus
        else:
            self.status = UnknownStatus


class FriendsParseRes(ParseRes):
    def __init__(self, friends: List[User], *args, **kwargs):
        self.friends = friends
        super().__init__(*args, **kwargs)


class GroupsParseRes(ParseRes):
    def __init__(self, groups: List[Group], *args, **kwargs):
        self.groups = groups
        super().__init__(*args, **kwargs)
