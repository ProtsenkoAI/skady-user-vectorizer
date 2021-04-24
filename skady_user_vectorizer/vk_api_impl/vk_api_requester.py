from typing import List

from interfaces import User, AccessErrorListener
from .requests import Request, GroupsRequest, FriendsRequest


class VkApiRequester(AccessErrorListener):
    # TODO: make requester an access error listener to re-request failed users (need to pass user in notify)
    # TODO: maybe add maximum of requests per call
    # TODO: refactor creation of users (use some generative pattern)
    def __init__(self):
        self.users_to_friends_request = []
        self.users_to_groups_request = []

    def add_users(self, users: List[User]):
        self.users_to_friends_request.extend(users)
        self.users_to_groups_request.extend(users)

    def get_requests(self) -> List[Request]:
        return self._request_friends_and_groups()

    def _request_friends_and_groups(self):
        requests = []
        while self.users_to_friends_request:
            user = self.users_to_friends_request.pop(0)
            requests.append(FriendsRequest(user))
        while self.users_to_friends_request:
            user = self.users_to_groups_request.pop(0)
            requests.append(GroupsRequest(user))
        return requests

    def access_error_occurred(self, user, type_of_request: str, *args, **kwargs):
        if type_of_request == "friends":
            self.users_to_friends_request.append(user)
        elif type_of_request == "groups":
            self.users_to_groups_request.append(user)
        else:
            raise ValueError(f"Unknown type_of_request: {type_of_request}")
