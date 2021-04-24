from typing import List

from interfaces import ParsedProcessor, DataManager, User, Tracker, FriendsParseRes, GroupsParseRes
from interfaces import SuccessParseStatus, AccessErrorStatus, ParseStatus


class ParsedProcessorImpl(ParsedProcessor):
    # TODO: stop parsing if parsed enough users
    def __init__(self, data_manager: DataManager, progress_tracker: Tracker):
        self.data_manager = data_manager
        self.tracker = progress_tracker
        self.parse_candidates = []
        super().__init__()

    def proc_friends(self, friends_res: FriendsParseRes):
        status = friends_res.status
        if status == SuccessParseStatus:
            friends = friends_res.friends
            self.data_manager.save_user_friends(friends_res.user, friends)
            unparsed_friends = self.data_manager.filter_already_seen_users(friends)
            self.parse_candidates += unparsed_friends
            self.tracker.friends_added(len(friends))
        else:
            self._proc_non_success_status(status)

    def proc_groups(self, groups_res: GroupsParseRes):
        status = groups_res.status
        if status == SuccessParseStatus:
            groups = groups_res.groups
            self.data_manager.save_user_groups(groups_res.user, groups)
            self.tracker.groups_added(len(groups))
        else:
            self._proc_non_success_status(status)

    def get_new_parse_candidates(self) -> List[User]:
        val = self.parse_candidates
        self.parse_candidates = []
        return val

    def _proc_non_success_status(self, status: ParseStatus):
        if status == AccessErrorStatus:
            self.notify_access_error_listeners()
        else:
            raise ValueError(f"Unknown status {status}")
