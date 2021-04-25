from interfaces import RequestsCreator, User
from .requests import FriendsRequest, GroupsRequest


class VkApiRequestsCreator(RequestsCreator):
    def friends_request(self, candidate: User):
        return FriendsRequest(candidate)

    def groups_request(self, candidate: User):
        return GroupsRequest(candidate)
