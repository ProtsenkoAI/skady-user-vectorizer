import vk_api

from suvec.common.executing import Response
from suvec.common.requesting import Request


class FriendsRequest(Request):
    def get_method(self) -> str:
        return "friends.get"

    def create_response(self, resp_raw: vk_api.requests_pool.RequestResult) -> Response:
        return self.responses_factory.create_friends_response(resp_raw, user=self.user)


class GroupsRequest(Request):
    def get_method(self) -> str:
        return "groups.get"

    def create_response(self, resp_raw: vk_api.requests_pool.RequestResult) -> Response:
        return self.responses_factory.create_groups_response(resp_raw, user=self.user)
