from typing import List

from ..listen_notify import RequestSuccessListener, AccessErrorListener
from .base_requester import BaseRequester
from ..top_level_types import User
from .requested_users_storage import RequestedUsersFileStorage
from .users_filter import DuplicateUsersFilter
from .request import Request


class EconomicRequester(BaseRequester, RequestSuccessListener, AccessErrorListener):
    """When user is added, first schedules one type of request and if it succeeds sends all other.
    Also checks that users are unique"""
    def __init__(self, *args, friends_req_storage: RequestedUsersFileStorage,
                 groups_req_storage: RequestedUsersFileStorage,
                 users_filter: DuplicateUsersFilter,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.friends_req_storage = friends_req_storage
        self.groups_req_storage = groups_req_storage
        self.users_filter = users_filter

    def add_users(self, users: List[User]):
        filtered_users = self.users_filter(users)
        for user in filtered_users:
            self.friends_req_storage.add_user(user)

    def get_requests(self) -> List[Request]:
        users_to_friends_request = self.friends_req_storage.get_users(self.max_requests_per_call)
        friends_requests = self.create_friends_requests(users_to_friends_request)

        users_needed = self.max_requests_per_call - len(friends_requests)
        if users_needed > 0:
            users_to_groups_request = self.groups_req_storage.get_users(users_needed)
            groups_requests = self.create_groups_requests(users_to_groups_request)
        else:
            groups_requests = []

        return friends_requests + groups_requests

    def request_succeed(self, user: User, req_type: str):
        if req_type == "groups":
            self.groups_req_storage.add_user(user)

    def access_error_occurred(self, parse_res):
        if parse_res.request_type == "friends":
            self.friends_req_storage.add_user(parse_res.request.user)
        elif parse_res.request_type == "groups":
            self.groups_req_storage.add_user(parse_res.request.user)
        else:
            raise ValueError(f"Unknown type_of_request: {parse_res.request_type}")

    def get_checkpoint(self):
        groups_req_data = self.groups_req_storage.get_checkpoint()
        friends_req_data = self.friends_req_storage.get_checkpoint()
        filter_data = self.users_filter.get_checkpoint()
        return groups_req_data, friends_req_data, filter_data

    def load_checkpoint(self, checkp_data):
        groups_req_data, friends_req_data, filter_data = checkp_data

        self.groups_req_storage.load_checkpoint(groups_req_data)
        self.friends_req_storage.load_checkpoint(friends_req_data)
        self.users_filter.load_checkpoint(filter_data)
