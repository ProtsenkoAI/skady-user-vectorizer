from abc import ABC, abstractmethod
from typing import Optional
import logging
import sys

from ..top_level_types import User
from ..utils import AbstractSingleton


class EventsTracker(ABC, metaclass=AbstractSingleton):
    # LATER_TODO: need tracker checkpoints if robust stats are needed

    def __init__(self, log_pth: str):
        logging.basicConfig(filename=log_pth, level="INFO")
        self.logger = logging.getLogger("suvec.vk_api_impl.EventsTrackerLogger")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))  # also print logs to stdout

    @abstractmethod
    def error_occurred(self, description: str):
        ...

    @abstractmethod
    def skip_user(self, user: User, msg: Optional[str] = None):
        ...

    @abstractmethod
    def user_parsed(self):
        ...

    @abstractmethod
    def creds_changed(self):
        ...

    @abstractmethod
    def proxy_changed(self):
        ...
