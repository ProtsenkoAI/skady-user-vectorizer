from typing import List

from .parse_res import ParseRes, FriendsParseRes, GroupsParseRes
from interfaces import ParsedEnoughNotifier, AccessErrorNotifier, DataManager, Tracker, User

from .error_codes import ACCESS_ERROR_CODE


class VkApiParsedProcessor(ParsedEnoughNotifier, AccessErrorNotifier):
    # TODO: union with processor impl from common_components/
    def __init__(self, data_manager: DataManager, progress_tracker: Tracker, max_users: int = 10000):
        self.data_manager = data_manager
        self.tracker = progress_tracker
        self.parse_candidates = []
        self.max_users = max_users

        ParsedEnoughNotifier.__init__(self)
        AccessErrorNotifier.__init__(self)

    def process(self, parsed_results: ParseRes):
        if parsed_results.error:
            self._process_res_with_error(parsed_results)
        else:
            if parsed_results.request_type == "friends":
                parsed_results: FriendsParseRes
                self._proc_friends(parsed_results)
            elif parsed_results.request_type == "groups":
                parsed_results: GroupsParseRes
            else:
                raise ValueError(f"Unknown request_type: {parsed_results.request_type}")

    def _process_res_with_error(self, parsed_results: ParseRes):
        if parsed_results.error.code == ACCESS_ERROR_CODE:
            self.notify_access_error_listeners(user=parsed_results.user,
                                               type_of_request=parsed_results.request_type)
        else:
            # TODO: maybe not rise error, but log (to continue crawl and save results despite raised errors
            raise ValueError(f"Unknown error occurred: {parsed_results.error.code}.from"
                             f"User: {parsed_results.user}, Error obj: {parsed_results.error}")

    def _proc_friends(self, results: FriendsParseRes):
        friends = results.friends
        self.data_manager.save_user_friends(results.user, friends)
        unparsed_friends = self.data_manager.filter_already_seen_users(friends)
        self.parse_candidates += unparsed_friends
        # TODO: refactor tracker interface
        self.tracker.friends_added(len(friends))

        if self.max_users <= self.data_manager.get_num_users():
            self.notify_parsed_enough_listeners()

    def _proc_groups(self, results: GroupsParseRes):
        groups = results.groups
        self.data_manager.save_user_groups(results.user, groups)
        self.tracker.groups_added(len(groups))

    def get_new_parse_candidates(self) -> List[User]:
        val = self.parse_candidates
        self.parse_candidates = []
        return val
