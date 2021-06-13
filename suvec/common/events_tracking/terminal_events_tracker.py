import time
from typing import Optional
from ..top_level_types import User
from ..utils import Singleton
from .base_events_tracker import EventsTracker


class TerminalEventsTracker(EventsTracker, metaclass=Singleton):
    # be careful with this singleton
    def __init__(self, log_pth: str, report_every_responses_nb: int = 1000):
        super().__init__(log_pth)
        self.report_every_responses_nb = report_every_responses_nb

        self.errors_cnt = 0

        self.nb_users_parsed = 0
        self.requests_parsed_since_proxy_change = 0
        self.requests_parsed_since_creds_change = 0
        self.prev_report_time = time.time()

        self.skipped_users_cnt = 0

    def error_occurred(self, description: str):
        super().error_occurred(description)

    def skip_user(self, user: User, msg: Optional[str] = None):
        self.skipped_users_cnt += 1
        self._request_parsed()

    def user_parsed(self):
        self._request_parsed()
        self.nb_users_parsed += 1

    def _request_parsed(self):
        self.requests_parsed_since_creds_change += 1
        self.requests_parsed_since_proxy_change += 1

    def state_report(self):
        time_passed = time.time() - self.prev_report_time
        # TODO: maybe save full list of skipped users and reasons somewhere
        # TODO: check that nb users parsed in logs is adequate
        msg_lines = (f"State Report",
                     f"Nb users parsed: {self.nb_users_parsed}",
                     f"Total errors: {self.errors_cnt}",
                     f"Number of skipped users: {self.skipped_users_cnt}",
                     f"Seconds since previous report: {time_passed}")
        msg = "\n".join(msg_lines)

        self.logger.info(msg)
        self.prev_report_time = time.time()

    def creds_changed(self):
        self.requests_parsed_since_creds_change = 0

    def proxy_changed(self):
        self.requests_parsed_since_proxy_change = 0
