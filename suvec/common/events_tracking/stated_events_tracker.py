import time
from typing import TypedDict, List, Optional
from .base_events_tracker import EventsTracker
from ..top_level_types import User, Group
from ..executing import ErrorObj


class TrackerState(TypedDict):
    parse_speed: List[float]
    cur_session_requests: int
    mean_session_lifetime: Optional[float]
    working_proxies_cnt: Optional[int]
    working_creds_cnt: Optional[int]
    used_proxies_cnt: int
    used_creds_cnt: int
    users_parsed: int
    errors_cnt: int
    total_groups: int


class StatedEventsTracker(EventsTracker):
    # TODO: need to get working_proxies_cnt and working_creds_cnt at init stage from storages
    # TODO: separate creds session change and proxy session change
    # TODO: maybe delete friends added and groups added methods
    def __init__(self, log_pth: str, num_parse_speed_points_stored: int = 200):
        super().__init__(log_pth)
        self._sessions_requests_cnt = []
        self._parsed_users: List[User] = []
        self.num_parse_speed_points_stored = num_parse_speed_points_stored
        self.state = TrackerState(parse_speed=[],
                                  cur_session_requests=0,
                                  mean_session_lifetime=None,
                                  working_proxies_cnt=None,
                                  working_creds_cnt=None,
                                  used_creds_cnt=0,
                                  used_proxies_cnt=0,
                                  users_parsed=0,
                                  errors_cnt=0,
                                  total_groups=0
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

    def error_occurred(self, error: ErrorObj, msg: Optional[str] = None):
        self.state["errors_cnt"] += 1
        super().error_occurred(error, msg)

    def skip_user(self, user: User, msg: Optional[str] = None):
        self._request_processed()

    def friends_added(self, user: User, friends: List[User]):
        self._request_processed()
        self._count_user_if_all_requests_parsed(user)

    def groups_added(self, user: User, groups: List[Group]):
        self._request_processed()
        self.state["total_groups"] += len(groups)
        self._count_user_if_all_requests_parsed(user)

    def _count_user_if_all_requests_parsed(self, user: User):
        if user in self._parsed_users:
            self.state["users_parsed"] += 1
            self._parsed_users.remove(user)
        else:
            self._parsed_users.append(user)

    def creds_report(self, creds_left, creds_can_be_used, changed):
        if changed:
            self.state["working_creds_cnt"] = creds_can_be_used
            self.state["used_creds_cnt"] = creds_left - creds_can_be_used

    def proxy_report(self, proxy_left: int, proxy_left_with_ok_state: int, changed):
        if changed:
            self._sessions_requests_cnt.append(self.state["cur_session_requests"])
            self.state["cur_session_requests"] = 0
            self.state["mean_session_lifetime"] = self._mean(self._sessions_requests_cnt)
            self.state["working_proxies_cnt"] = proxy_left_with_ok_state
            self.state["used_proxies_cnt"] = proxy_left - proxy_left_with_ok_state

    def loop_started(self):
        self.start_loop_time = time.time()
        self.loop_requests = 0

    def report_long_term_data_stats(self, users_parsed: int, total_groups: int):
        self.state["users_parsed"] = users_parsed
        self.state["total_groups"] = total_groups

    def loop_ended(self):
        time_for_loop = time.time() - self.start_loop_time
        self.state["parse_speed"].append(self.loop_requests / time_for_loop)
        self.state["parse_speed"] = self.state["parse_speed"][-self.num_parse_speed_points_stored:]

    def _mean(self, lst):
        if len(lst):
            return sum(lst) / len(lst)
        return 0
