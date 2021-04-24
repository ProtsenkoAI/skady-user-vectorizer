from abc import ABC, abstractmethod
from typing import List

from .top_level_types import User
from .parse_res import FriendsParseRes, GroupsParseRes
from .parsed_enough_notifier import ParsedEnoughNotifier
from .access_error_notifier import AccessErrorNotifier


class ParsedProcessor(ABC, ParsedEnoughNotifier, AccessErrorNotifier):
    def __init__(self):
        ParsedEnoughNotifier.__init__(self)
        AccessErrorNotifier.__init__(self)
        
    @abstractmethod
    def proc_friends(self, friends: FriendsParseRes):
        ...

    @abstractmethod
    def proc_groups(self, groups: GroupsParseRes):
        ...

    @abstractmethod
    def get_new_parse_candidates(self) -> List[User]:
        ...
