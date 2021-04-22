from typing import Iterable

from ..interfaces import Requester, Parser, ParsedProcessor, User, RequestsCreator, AccessErrorListener


class CallbackRequester(Requester, AccessErrorListener):
    """Requests info about new users and sets it's own methods as request callbacks to get new users
    and the request them"""
    def __init__(self, parser: Parser, parsed_processor: ParsedProcessor, requests_creator: RequestsCreator):
        self.parser = parser
        self.parsed_processor = parsed_processor
        self.parse_candidates = []
        self.dumped_candidates = []
        self.requests_creator = requests_creator

        self.is_authorized = False

        self.parsed_processor.register_access_error_listener(self)

    def access_error_occurred(self):
        self.is_authorized = False
        self.requests_creator.change_proxy()
        self.dumped_candidates = self.parse_candidates
        self.parse_candidates = []

    def get_requests(self) -> Iterable:
        if not self.is_authorized:
            return self.requests_creator.auth_request(callback=self.auth_callback)

        candidates = self.parse_candidates
        self.parse_candidates = []

        requests = []
        for candidate in candidates:
            requests.extend(self._form_user_requests(candidate))
        return requests

    def _form_user_requests(self, candidate: User) -> Iterable:
        friends_request = self.requests_creator.friends_request(candidate, callback=self.friends_callback)
        groups_request = self.requests_creator.groups_request(candidate, callback=self.groups_callback)
        return friends_request, groups_request

    def add_users(self, users: Iterable[User]):
        self.parse_candidates.extend(users)

    def friends_callback(self, response):
        friends_parsed = self.parser.parse_friends(response)
        self.parsed_processor.proc_friends(friends_parsed)

        new_users_to_parse = self.parsed_processor.get_new_parse_candidates()
        self.add_users(new_users_to_parse)

    def groups_callback(self, response):
        groups_parsed = self.parser.parse_groups(response)
        self.parsed_processor.proc_groups(groups_parsed)

    def auth_callback(self, response):
        auth_success = self.parser.check_auth_success(response)
        if auth_success:
            self.parse_candidates.extend(self.dumped_candidates)
            self.dumped_candidates = []
            self.is_authorized = True
