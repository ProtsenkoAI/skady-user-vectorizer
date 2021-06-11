from typing import List

from ..listen_notify import RequestSuccessListener
from .base_requester_impl import BaseRequesterImpl
from ..top_level_types import User


class EconomicRequester(BaseRequesterImpl, RequestSuccessListener):
    """When user is added, first schedules one type of request and if it succeeds sends all other.
    Also checks that users are unique"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.already_added = set()

    def add_users(self, users: List[User]):
        unseen_users = set(users).difference(self.already_added)
        self.users_to_groups_request += unseen_users
        self.already_added.update(unseen_users)

    def request_succeed(self, user: User, req_type: str):
        if req_type == "groups":
            self.users_to_friends_request.append(user)
