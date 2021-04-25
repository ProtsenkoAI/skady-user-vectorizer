import logging, time
from typing import Optional, List
from collections import defaultdict

from .parse_res import VkApiErrorObj
from interfaces import User, Group
from common_components import Singleton


class EventsTracker(metaclass=Singleton):
    # NOTE: it's dirty class with many specific methods, so please don't subclass it, otherwise you
    #   will sink in problems with rewriting each subclass. It's made in this style because of
    #   simplicity of realisation and ease of use from other objects side.
    # TODO: refactor
    # TODO: count number of requests and reset credentials with proxy each N requests (call notify)
    # TODO: test that if imported in 2 different modules will have only one instance (it's quite unobvious
    #   how this is supposed to work)
    def __init__(self, log_pth: str, report_every_responses_nb: int = 1000):
        self.report_every_responses_nb = report_every_responses_nb

        logging.basicConfig(filename=log_pth)
        self.logger = logging.getLogger("skady_user_vectorizer.vk_api_impl.EventsTrackerLogger")

        self.errors = []
        self.errors_cnt = defaultdict(int)
        self.skip_user_reasons: List[str] = []
        self.skipped_users: List[User] = []

        self.groups_responses_cnt = 0
        self.requests_parsed_since_proxy_change = 0
        self.requests_parsed_since_creds_change = 0
        self.total_groups_nb = 0
        self.total_friends_nb = 0
        self.prev_report_time = time.time()

    def error_occurred(self, error: VkApiErrorObj, msg: Optional[str] = None):
        self.logger.error(f"status code: {error.code}, msg: {msg}, error obj: {error.error}")
        self.errors_cnt[error.code] += 1
        self.errors.append(error)

    def skip_user(self, user: User, msg: Optional[str] = None):
        self.skipped_users.append(user)
        self.skip_user_reasons.append(msg)

    def message(self, msg: str):
        self.logger.info(msg)

    def friends_added(self, friends: List[User]):
        self.total_friends_nb += len(friends)
        self.requests_parsed_since_creds_change += 1
        self.requests_parsed_since_proxy_change += 1
        self._maybe_state_report()

    def groups_added(self, groups: List[Group]):
        self.total_groups_nb += len(groups)
        self.groups_responses_cnt += 1
        self.requests_parsed_since_creds_change += 1
        self.requests_parsed_since_proxy_change += 1
        self._maybe_state_report()

    def _maybe_state_report(self):
        if self.groups_responses_cnt % self.report_every_responses_nb == 0:
            time_passed = int(time.time() - self.prev_report_time)
            self._state_report(time_passed)

    def _state_report(self, time_passed: int):
        # TODO: maybe save full list of skipped users and reasons somewhere
        msg = (f"State Report"
               f"Nb users parsed: {self.groups_responses_cnt}"
               f"Total errors: {len(self.errors)}"
               f"Errors counts by code: {self.errors_cnt}"
               f"Number of skipped users: {len(self.skipped_users)}"
               f"Seconds since previous report: {time_passed}"
               f"Total friends: {self.total_friends_nb}"
               f"Total Groups: {self.total_groups_nb}")
        self.logger.info(msg)

    def creds_report(self, creds_left, creds_can_be_used, changed):
        if changed:
            self.requests_parsed_since_creds_change = 0
        self._log_std_access_info_report("Creds", changed, creds_left, creds_can_be_used)

    def proxy_report(self, proxy_left: int, proxy_left_with_ok_state: int, changed):
        if changed:
            self.requests_parsed_since_proxy_change = 0
        self._log_std_access_info_report("Proxy", changed, proxy_left, proxy_left_with_ok_state)

    def _log_std_access_info_report(self, report_name, changed, left, usable_left):
        msg = (f"{report_name} report. "
               f"Changed: {changed}"
               f"Total: {left}, {usable_left} of them are marked as usable"
               )
        self.logger.info(msg)
