import time
from typing import TypedDict, List, Optional
from .base_events_tracker import EventsTracker
from ..top_level_types import User
from suvec.common import utils


class TrackerState(TypedDict):
    parse_speed: List[float]
    cur_session_requests: int
    mean_session_lifetime: Optional[float]
    users_parsed: int
    errors_cnt: int
    creds_used: int
    proxy_used: int


class StatedEventsTracker(EventsTracker):
    # TODO: need to get working_proxies_cnt and working_creds_cnt at init stage from storages
    # TODO: separate creds session change and proxy session change
    # TODO: maybe delete friends added and groups added methods
    def __init__(self, log_pth: str, num_parse_speed_points_stored: int = 200):
        super().__init__(log_pth)
        self._sessions_requests_cnt = []
        self.num_parse_speed_points_stored = num_parse_speed_points_stored
        self.state = TrackerState(parse_speed=[],
                                  cur_session_requests=0,
                                  mean_session_lifetime=None,
                                  users_parsed=0,
                                  errors_cnt=0,
                                  creds_used=0,
                                  proxy_used=0
                                  )
        self.prev_request_time = time.time()
        self.start_loop_time = None
        self.loop_requests = 0

    def get_state(self) -> TrackerState:
        return self.state

    def _request_processed(self):
        self.state["cur_session_requests"] += 1
        self.loop_requests += 1
        self.prev_request_time = time.time()

    def error_occurred(self, msg: str):
        self.state["errors_cnt"] += 1
        super().error_occurred(msg)

    def skip_user(self, user: User, msg: Optional[str] = None):
        self._request_processed()

    def user_parsed(self):
        self._request_processed()
        self.state["users_parsed"] += 1

    def creds_changed(self):
        self.state["creds_used"] += 1

    def proxy_changed(self):
        self.state["proxy_used"] += 1
        self._sessions_requests_cnt.append(self.state["cur_session_requests"])
        self.state["cur_session_requests"] = 0
        self.state["mean_session_lifetime"] = utils.safe_mean(self._sessions_requests_cnt)
