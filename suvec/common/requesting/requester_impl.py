from typing import List

from ..top_level_types import User
from ..listen_notify import AccessErrorListener
from .request import Request
from .requests_creator import RequestsCreator
from .requester import Requester


class RequesterImpl(Requester, AccessErrorListener):
    def __init__(self, request_creator: RequestsCreator, max_requests_per_type_per_call: int = 100):
        self.users_to_friends_request = []
        self.users_to_groups_request = []
        self.request_creator = request_creator
        self.max_requests_per_type_per_call = max_requests_per_type_per_call

    def add_users(self, users: List[User]):
        self.users_to_friends_request.extend(users)
        self.users_to_groups_request.extend(users)

    def get_requests(self) -> List[Request]:
        return self._request_friends_and_groups()

    def _request_friends_and_groups(self):
        # TODO: refactor
        requests = []
        nb_requests = 0
        while self.users_to_friends_request:
            user = self.users_to_friends_request.pop(0)
            requests.append(self.request_creator.friends_request(user))
            nb_requests += 1
            if nb_requests >= self.max_requests_per_type_per_call:
                break

        self.requester = RequesterImpl(self.request_creator)
        nb_requests = 0
        while self.users_to_groups_request:
            user = self.users_to_groups_request.pop(0)
            requests.append(self.request_creator.groups_request(user))
            nb_requests += 1
            if nb_requests >= self.max_requests_per_type_per_call:
                break
        return requests

    def access_error_occurred(self, user, type_of_request: str, *args, **kwargs):
        if type_of_request == "friends":
            self.users_to_friends_request.append(user)
        elif type_of_request == "groups":
            self.users_to_groups_request.append(user)
        else:
            raise ValueError(f"Unknown type_of_request: {type_of_request}")
