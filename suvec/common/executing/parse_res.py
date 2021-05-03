from abc import ABC
from typing import Optional, List

from suvec.common.top_level_types import User, Group
from .types import ErrorObj


class ParseRes(ABC):
    def __init__(self, user: User, request_type: str, error: Optional[ErrorObj] = None):
        self.user = user
        self.request_type = request_type
        self.error = error


class FriendsParseRes(ParseRes):
    def __init__(self, user: User, friends: Optional[List[User]] = None, error: Optional[ErrorObj] = None):
        super().__init__(user, "friends", error)
        self.friends = friends
        if self.friends is None and self.error is None:
            raise ValueError("Should provide friends or error, but both are None")


class GroupsParseRes(ParseRes):
    def __init__(self, user: User, groups: Optional[List[Group]] = None, error: Optional[ErrorObj] = None):
        super().__init__(user, "groups", error)
        self.groups = groups
        if self.groups is None and self.error is None:
            raise ValueError("Should provide groups or error, but both are None")
