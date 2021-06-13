from suvec.common.top_level_types import User
from suvec.common.requesting import RequestsCreator
from .requests import FriendsRequest, GroupsRequest


class VkApiRequestsCreator(RequestsCreator):
    def friends_request(self, candidate: User):
        return FriendsRequest(candidate, req_type="friends")

    def groups_request(self, candidate: User):
        return GroupsRequest(candidate, req_type="groups")
