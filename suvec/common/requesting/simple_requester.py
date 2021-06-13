from typing import List

from .request import Request
from suvec.common.top_level_types import User
from .base_requester import BaseRequester


class SimpleRequester(BaseRequester):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users_to_friends_request = []
        self.users_to_groups_request = []

    def add_users(self, users: List[User]):
        self.users_to_friends_request.extend(users)
        self.users_to_friends_request = list(set(self.users_to_friends_request))

        self.users_to_groups_request.extend(users)
        self.users_to_groups_request = list(set(self.users_to_groups_request))

    def get_requests(self) -> List[Request]:
        requests = []
        requests += self.create_friends_requests(self.users_to_friends_request[:self.max_requests_per_call])
        # Friends requests is first priority, then go groups requests
        requests_left = self.max_requests_per_call - len(requests)
        requests += self.create_groups_requests(self.users_to_groups_request[:requests_left])

        self.users_to_friends_request = self.users_to_friends_request[self.max_requests_per_call:]
        self.users_to_groups_request = self.users_to_groups_request[requests_left:]

        return requests
