from abc import ABC, abstractmethod
from typing import Callable, List, Any, Iterable
from .processed_user_res import UserFriendsRes
from .parse_statuses import SUCCESS

from global_types import User


class RequestsCreator(ABC):
    # TODO: make abstract and move specifics to impl
    Request = Any

    def __init__(self, user_friends_hook: Callable, user_groups_hook: Callable):
        """Hooks are methods (NOT OF SCRAPY SPIDER, JUST OBJECT THAT HANDLES SAVING, LOGING ETC)
        that will be called on responses"""
        self.user_friends_hook = user_friends_hook
        self.user_groups_hook = user_groups_hook
        self.planned_requests = []
        self.queued_requests = []

    def add_users(self, parsed_friends: UserFriendsRes):

        if parsed_friends.status == SUCCESS:
            self.planned_requests += self._create_users_requests(parsed_friends.friends)
        else:
            self.queued_requests = self.planned_requests
            self.planned_requests = [self.get_authorization_request()]

    def get_new_requests(self):
        return self.planned_requests

    def _create_users_requests(self, *users) -> List[Request]:
        out = []
        for user in users:
            out.append(self.make_friends_request(user))
            out.append(self.make_groups_request(user))
        return out

    # TODO: maybe move these to impl
    @abstractmethod
    def make_friends_request(self, user: User) -> Request:
        ...

    @abstractmethod
    def make_groups_request(self, user: User) -> Request:
        ...

    @abstractmethod
    def get_authorization_request(self):
        ...

    @abstractmethod
    def friends_callback(self):
        ...

    @abstractmethod
    def groups_callback(self):
        ...

    @abstractmethod
    def authorization_callback(self):
        ...
