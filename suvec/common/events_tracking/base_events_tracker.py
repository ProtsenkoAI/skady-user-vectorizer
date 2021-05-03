from abc import ABC, abstractmethod
from typing import Optional, List
import logging
import sys

from ..executing import ErrorObj
from ..top_level_types import User, Group
from ..utils import AbstractSingleton


class EventsTracker(ABC, metaclass=AbstractSingleton):
    def __init__(self, log_pth: str):
        logging.basicConfig(filename=log_pth, level="INFO")
        self.logger = logging.getLogger("suvec.vk_api_impl.EventsTrackerLogger")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))  # also print logs to stdout

    @abstractmethod
    def error_occurred(self, error: ErrorObj, msg: Optional[str] = None):
        ...

    @abstractmethod
    def skip_user(self, user: User, msg: Optional[str] = None):
        ...

    def message(self, msg: str):
        self.logger.info(msg)

    @abstractmethod
    def friends_added(self, user: User, friends: List[User]):
        ...

    @abstractmethod
    def groups_added(self, user: User, groups: List[Group]):
        ...

    @abstractmethod
    def creds_report(self, creds_left, creds_can_be_used, changed):
        ...

    @abstractmethod
    def proxy_report(self, proxy_left: int, proxy_left_with_ok_state: int, changed):
        ...

    @abstractmethod
    def loop_started(self):
        ...

    @abstractmethod
    def loop_ended(self):
        ...
