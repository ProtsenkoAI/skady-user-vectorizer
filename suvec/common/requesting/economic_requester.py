from typing import List

from ..listen_notify.request_success import RequestSuccessListener
from .base_requester_impl import BaseRequesterImpl
from ..top_level_types import User


class EconomicRequester(BaseRequesterImpl, RequestSuccessListener):
    """When user is added, first schedules one type of request and if it succeeds sends all other"""
    def add_users(self, users: List[User]):
        self.users_to_groups_request += users

        self.users_to_groups_request = list(set(self.users_to_groups_request))
        self.users_to_friends_request = list(set(self.users_to_friends_request))

    def request_succeed(self, user: User, req_type: str):
        if req_type == "groups":
            self.users_to_friends_request.append(user)
