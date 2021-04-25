import logging
from typing import Optional, List
from collections import defaultdict

from .parse_res import VkApiErrorObj
from interfaces import User, Group
from common_components import Singleton


class EventsTracker(metaclass=Singleton):
    # NOTE: it's dirty class with many specific methods, so please don't subclass it, otherwise you
    #   will sink in problems with rewriting each subclass. It's made in this style because of
    #   simplicity of realisation and ease of use from other objects side.
    # TODO
    # TODO: count number of requests and reset credentials with proxy each N requests (call notify)
    # TODO: test that if imported in 2 different modules will have only one instance (it's quite unobvious
    #   how this is supposed to work)
    def __init__(self, log_pth: str):
        logging.basicConfig(filename=log_pth)
        self.logger = logging.getLogger("skady_user_vectorizer.vk_api_impl.EventsTrackerLogger")

        self.errors_cnt = defaultdict(int)
        self.skip_user_reasons: List[str] = []
        self.skipped_users: List[User] = []

    def error_occurred(self, error: VkApiErrorObj, msg: Optional[str] = None):
        self.logger.error(f"status code: {error.code}, msg: {msg}, error obj: {error.error}")
        self.errors_cnt[error.code] += 1

    def skip_user(self, user: User, msg: Optional[str] = None):
        self.skipped_users.append(user)
        self.skip_user_reasons.append(msg)

    def message(self, msg: str):
        self.logger.info(msg)

    def friends_added(self, friends: List[User]):
        # TODO
        ...

    def groups_added(self, groups: List[Group]):
        # TODO
        ...

    def new_credentials(self, email, password):
        ...

    def new_proxies(self, address: str, protocols: List[str]):
        ...
