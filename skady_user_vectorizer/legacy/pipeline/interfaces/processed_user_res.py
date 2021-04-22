from typing import List, Optional

from global_types import User, Group
from .parse_statuses import UserProcStatus


class ParseRes:
    def __init__(self, status: UserProcStatus, desc: Optional[str] = None):
        self.status = status
        self.desc = desc


class UserGroupsRes(ParseRes):
    def __init__(self, groups: List[Group], *args, **kwargs):
        self.groups = groups
        super().__init__(*args, **kwargs)


class UserFriendsRes(ParseRes):
    def __init__(self, friends: List[User], *args, **kwargs):
        self.friends = friends
        super().__init__(*args, **kwargs)
