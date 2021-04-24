from typing import List

from interfaces import User
from .requests import Request, GroupsRequest, FriendsRequest


class VkApiRequester:
    def __init__(self):
        self.users_to_request = []

    def add_users(self, users: List[User]):
        self.users_to_request.extend(users)

    def get_requests(self) -> List[Request]:
        raise NotImplementedError

    def auth_request(self):
        raise NotImplementedError
