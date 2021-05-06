
import time
from typing import Optional, List
from collections import defaultdict

from ..executing import ErrorObj
from ..top_level_types import User, Group
from ..utils import Singleton
from .base_events_tracker import EventsTracker


class TerminalEventsTracker(EventsTracker, metaclass=Singleton):
    # TODO: test that if imported in 2 different modules will have only one instance (it's singleton)
    def __init__(self, log_pth: str, report_every_responses_nb: int = 1000):
        super().__init__(log_pth)
        self.report_every_responses_nb = report_every_responses_nb

        self.errors_cnt = defaultdict(int)

        self.groups_responses_cnt = 0
        self.requests_parsed_since_proxy_change = 0
        self.requests_parsed_since_creds_change = 0
        self.total_groups_nb = 0
        self.prev_report_time = time.time()

        self.skipped_users_cnt = 0

    def error_occurred(self, error: ErrorObj, msg: Optional[str] = None):
        super().error_occurred(error, msg)
        self.errors_cnt[error.code] += 1

    def skip_user(self, user: User, msg: Optional[str] = None):
        self.skipped_users_cnt += 1

    def friends_added(self, user: User, friends: List[User]):
        self._request_parsed()

    def groups_added(self, user: User, groups: List[Group]):
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
                     f"Total errors: {self.errors_cnt}",
                     f"Errors counts by code: {self.errors_cnt}",
                     f"Number of skipped users: {self.skipped_users_cnt}",
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

    def loop_started(self):
        self.message("Starting new parsing loop")

    def loop_ended(self):
        self.message("Ending parsing loop")

    def report_long_term_data_stats(self, users_parsed: int, total_groups: int):
        self.total_groups_nb = total_groups
        self.groups_responses_cnt = users_parsed
