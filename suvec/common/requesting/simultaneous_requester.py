from typing import List

from .base_requester_impl import BaseRequesterImpl
from ..top_level_types import User


class SimultaneousRequester(BaseRequesterImpl):
    """When user is added, schedules all types of requests for him"""
    def add_users(self, users: List[User]):
        self.users_to_friends_request.extend(users)
        self.users_to_friends_request = list(set(self.users_to_friends_request))

        self.users_to_groups_request.extend(users)
        self.users_to_groups_request = list(set(self.users_to_groups_request))

