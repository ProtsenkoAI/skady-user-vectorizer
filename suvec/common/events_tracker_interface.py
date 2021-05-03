from abc import ABC, abstractmethod
from typing import Optional, List

from .executing import ErrorObj
from .top_level_types import User, Group
from .utils import AbstractSingleton


class EventsTracker(ABC, metaclass=AbstractSingleton):
    @abstractmethod
    def error_occurred(self, error: ErrorObj, msg: Optional[str] = None):
        ...

    @abstractmethod
    def skip_user(self, user: User, msg: Optional[str] = None):
        ...

    @abstractmethod
    def message(self, msg: str):
        ...

    @abstractmethod
    def friends_added(self, friends: List[User]):
        ...

    @abstractmethod
    def groups_added(self, groups: List[Group]):
        ...

    @abstractmethod
    def creds_report(self, creds_left, creds_can_be_used, changed):
        ...

    @abstractmethod
    def proxy_report(self, proxy_left: int, proxy_left_with_ok_state: int, changed):
        ...
