from typing import List

from .parse_res import ParseRes
from interfaces import ParsedEnoughNotifier, AccessErrorNotifier, DataManager, Tracker, User


class VkApiParsedProcessor(ParsedEnoughNotifier, AccessErrorNotifier):
    def __init__(self, data_manager: DataManager, progress_tracker: Tracker):
        self.data_manager = data_manager
        self.tracker = progress_tracker
        self.parse_candidates = []
        ParsedEnoughNotifier.__init__(self)
        AccessErrorNotifier.__init__(self)

    def process(self, parsed_results: List[ParseRes]):
        raise NotImplementedError

    def get_new_parse_candidates(self) -> List[User]:
        raise NotImplementedError
