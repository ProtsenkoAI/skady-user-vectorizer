from abc import ABC, abstractmethod
from .parse_res import FriendsParseRes, GroupsParseRes


class Parser(ABC):
    @abstractmethod
    def parse_friends(self, response) -> FriendsParseRes:
        ...

    @abstractmethod
    def parse_groups(self, response) -> GroupsParseRes:
        ...

    @abstractmethod
    def check_auth_success(self, response) -> bool:
        ...
