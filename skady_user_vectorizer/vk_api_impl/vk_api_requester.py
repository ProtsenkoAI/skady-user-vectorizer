from typing import List

from interfaces import User, AccessErrorListener, RequestsCreator
from .requests import Request


class VkApiRequester(AccessErrorListener):
    # IDEA: maybe add maximum of requests per call
    def __init__(self, request_creator: RequestsCreator):
        self.users_to_friends_request = []
        self.users_to_groups_request = []
        self.request_creator = request_creator

    def add_users(self, users: List[User]):
        self.users_to_friends_request.extend(users)
        self.users_to_groups_request.extend(users)

    def get_requests(self) -> List[Request]:
        return self._request_friends_and_groups()

    def _request_friends_and_groups(self):
        requests = []
        while self.users_to_friends_request:
            user = self.users_to_friends_request.pop(0)
            requests.append(self.request_creator.friends_request(user))
        while self.users_to_friends_request:
            user = self.users_to_groups_request.pop(0)
            requests.append(self.request_creator.groups_request(user))
        return requests

    def access_error_occurred(self, user, type_of_request: str, *args, **kwargs):
        if type_of_request == "friends":
            self.users_to_friends_request.append(user)
        elif type_of_request == "groups":
            self.users_to_groups_request.append(user)
        else:
            raise ValueError(f"Unknown type_of_request: {type_of_request}")
