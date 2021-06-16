from typing import List
import logging

from ..executing import ParseRes, FriendsParseRes, GroupsParseRes
from .data_managers import DataManager
from suvec.common.top_level_types import User
from suvec.common.events_tracking import EventsTracker
from suvec.common.external_errors_handling import ExternalErrorsHandler
from .parsed_processor import ParsedProcessor


class ParsedProcessorImpl(ParsedProcessor):
    def __init__(self, data_manager: DataManager, progress_tracker: EventsTracker,
                 errors_handler: ExternalErrorsHandler):
        self.data_manager = data_manager
        self.tracker = progress_tracker
        self.errors_handler = errors_handler
        self.parse_candidates = []

    def process(self, parsed_results: ParseRes, *args, **kwargs):
        if parsed_results.error:
            self.errors_handler.response_error(parsed_results)
        else:
            self.process_success(parsed_results)

    def process_success(self, res: ParseRes):
        if res.request_type == "friends":
            res: FriendsParseRes
            self._proc_friends(res)
        elif res.request_type == "groups":
            res: GroupsParseRes
            self._proc_groups(res)
        else:
            raise ValueError(f"Unknown request_type: {res.request_type}")

    def get_new_parse_candidates(self) -> List[User]:
        val = self.parse_candidates
        logging.info(f"Number of parse_candidates: {len(val)}")
        self.parse_candidates = []
        return val

    def _proc_friends(self, results: FriendsParseRes):
        friends = results.friends
        self.data_manager.save_user_friends(results.request.user, friends)
        self.parse_candidates += friends
        self.tracker.user_parsed()

    def _proc_groups(self, results: GroupsParseRes):
        groups = results.groups
        self.data_manager.save_user_groups(results.request.user, groups)
