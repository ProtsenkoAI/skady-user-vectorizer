from common.top_level_types import User
from common.requesting import RequestsCreator
from .requests import FriendsRequest, GroupsRequest


class VkApiRequestsCreator(RequestsCreator):
    def __init__(self, responses_factory):
        self.responses_factory = responses_factory

    def friends_request(self, candidate: User):
        return FriendsRequest(candidate, responses_factory=self.responses_factory)

    def groups_request(self, candidate: User):
        return GroupsRequest(candidate, responses_factory=self.responses_factory)
