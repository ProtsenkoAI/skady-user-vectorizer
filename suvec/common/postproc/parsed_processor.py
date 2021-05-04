from typing import List

from ..executing import ParseRes, FriendsParseRes, GroupsParseRes
from ..listen_notify import ParsedEnoughNotifier
from .data_managers import DataManager
from suvec.common.top_level_types import User


class ParsedProcessor(ParsedEnoughNotifier):
    def __init__(self, data_manager: DataManager, progress_tracker, errors_handler,
                 max_users: int = 10000):
        self.data_manager = data_manager
        self.tracker = progress_tracker
        self.errors_handler = errors_handler
        self.parse_candidates = []
        self.max_users = max_users

        ParsedEnoughNotifier.__init__(self)

    def process(self, parsed_results: ParseRes):
        if parsed_results.error:
            self.errors_handler.api_response_error(parsed_results)
        else:
            if parsed_results.request_type == "friends":
                parsed_results: FriendsParseRes
                self._proc_friends(parsed_results)
            elif parsed_results.request_type == "groups":
                parsed_results: GroupsParseRes
                self._proc_groups(parsed_results)
            else:
                raise ValueError(f"Unknown request_type: {parsed_results.request_type}")

    def get_new_parse_candidates(self) -> List[User]:
        val = self.parse_candidates
        self.tracker.message(f"Number of parse_candidates: {len(val)}")
        self.parse_candidates = []
        return val

    def _proc_friends(self, results: FriendsParseRes):
        friends = results.friends
        self.data_manager.save_user_friends(results.user, friends)
        unparsed_friends = self.data_manager.filter_already_seen_users(friends)
        self.parse_candidates += unparsed_friends
        self.tracker.friends_added(friends=unparsed_friends, user=results.user)

        if self.max_users <= self.data_manager.get_num_users():
            self.notify_parsed_enough()

    def _proc_groups(self, results: GroupsParseRes):
        groups = results.groups
        self.data_manager.save_user_groups(results.user, groups)
        self.tracker.groups_added(groups=groups, user=results.user)
