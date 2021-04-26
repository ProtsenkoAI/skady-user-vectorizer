from interfaces import RequestsCreator, User
from .vk_api_specific.requests import FriendsRequest, GroupsRequest


class VkApiRequestsCreator(RequestsCreator):
    def __init__(self, responses_factory):
        self.responses_factory = responses_factory

    def friends_request(self, candidate: User):
        return FriendsRequest(candidate, responses_factory=self.responses_factory)

    def groups_request(self, candidate: User):
        return GroupsRequest(candidate, responses_factory=self.responses_factory)
