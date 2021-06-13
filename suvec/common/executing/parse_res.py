from abc import ABC
from typing import Optional, List

from suvec.common.top_level_types import User, Group
from suvec.common.requesting import Request
from .types import ErrorObj


class ParseRes(ABC):
    def __init__(self, request_type: str, request: Request, error: Optional[ErrorObj] = None,
                 session_id: Optional[int] = None):
        self.request_type = request_type
        self.error = error
        self.request = request
        self.session_id = session_id


class FriendsParseRes(ParseRes):
    def __init__(self, friends: Optional[List[User]], request: Request, error: Optional[ErrorObj] = None, **kwargs):
        super().__init__(request_type="friends", error=error, request=request, **kwargs)
        self.friends = friends
        if self.friends is None and self.error is None:
            raise ValueError("Should provide friends or error, but both are None")


class GroupsParseRes(ParseRes):
    def __init__(self, groups: Optional[List[Group]], request: Request, error: Optional[ErrorObj] = None, **kwargs):
        super().__init__("groups", error=error, request=request, **kwargs)
        self.groups = groups
        if self.groups is None and self.error is None:
            raise ValueError("Should provide groups or error, but both are None")
