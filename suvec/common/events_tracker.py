import logging
import time
import sys
from typing import Optional, List
from collections import defaultdict

from .executing import ErrorObj
from .top_level_types import User, Group
from .utils import Singleton


class EventsTracker(metaclass=Singleton):
    # NOTE: it's dirty class with many specific methods, so please don't subclass it, otherwise you
    #   will sink in problems with rewriting each subclass. It's made in this style because of
    #   simplicity of realisation and ease of use from other objects side.
    # TODO: if will frequently add new methods for tracking will need to move state object with operations like
    #   log, form request, etc to sep component and create many specific classes for each type of tracking

    # TODO: test that if imported in 2 different modules will have only one instance
    def __init__(self, log_pth: str, report_every_responses_nb: int = 1000):
        self.report_every_responses_nb = report_every_responses_nb

        logging.basicConfig(filename=log_pth, level="INFO")
        self.logger = logging.getLogger("suvec.vk_api_impl.EventsTrackerLogger")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))  # also print logs to stdout

        self.errors = []
        self.errors_cnt = defaultdict(int)
        self.skip_user_reasons: List[str] = []
        self.skipped_users: List[User] = []

        self.groups_responses_cnt = 0
        self.requests_parsed_since_proxy_change = 0
        self.requests_parsed_since_creds_change = 0
        self.total_groups_nb = 0
        self.prev_report_time = time.time()

    def error_occurred(self, error: ErrorObj, msg: Optional[str] = None):
        self.logger.error(f"status code: {error.code}, msg: {msg}, error obj: {error.error}")
        self.errors_cnt[error.code] += 1
        self.errors.append(error)

    def skip_user(self, user: User, msg: Optional[str] = None):
        self.skipped_users.append(user)
        self.skip_user_reasons.append(msg)

    def message(self, msg: str):
        self.logger.info(msg)

    def friends_added(self, friends: List[User]):
        self._request_parsed()

    def groups_added(self, groups: List[Group]):
        self.total_groups_nb += len(groups)
        self.groups_responses_cnt += 1
        self._request_parsed()

    def _request_parsed(self):
        self.requests_parsed_since_creds_change += 1
        self.requests_parsed_since_proxy_change += 1
        self._maybe_state_report()

    def _maybe_state_report(self):
        if self.groups_responses_cnt % self.report_every_responses_nb == 0:
            time_passed = time.time() - self.prev_report_time
            self.prev_report_time = time.time()
            self._state_report(time_passed)

    def _state_report(self, time_passed: float):
        # TODO: maybe save full list of skipped users and reasons somewhere
        # TODO: check that nb users parsed in logs is adequate
        msg_lines = (f"State Report",
                     f"Nb users parsed: {self.groups_responses_cnt}",
                     f"Total errors: {len(self.errors)}",
                     f"Errors counts by code: {self.errors_cnt}",
                     f"Number of skipped users: {len(self.skipped_users)}",
                     f"Seconds since previous report: {time_passed}",
                     f"Total Groups: {self.total_groups_nb}")
        msg = "\n".join(msg_lines)

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
        msg_lines = (f"{report_name} report.",
                     f"Changed: {changed}",
                     f"Total: {left}, {usable_left} of them are marked as usable"
                     )
        msg = "\n".join(msg_lines)
        self.logger.info(msg)
