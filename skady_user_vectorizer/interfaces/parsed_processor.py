from abc import ABC, abstractmethod
from typing import List

from .access_error_listener import AccessErrorListener
from .top_level_types import User
from .parse_res import FriendsParseRes, GroupsParseRes


class ParsedProcessor(ABC):
    def __init__(self):
        self.access_error_listeners: List[AccessErrorListener] = []

    @abstractmethod
    def proc_friends(self, friends: FriendsParseRes):
        ...

    @abstractmethod
    def proc_groups(self, groups: GroupsParseRes):
        ...

    @abstractmethod
    def get_new_parse_candidates(self) -> List[User]:
        ...

    def register_access_error_listener(self, listener: AccessErrorListener):
        self.access_error_listeners.append(listener)

    def notify_access_error_listeners(self):
        for listener in self.access_error_listeners:
            listener.access_error_occurred()
