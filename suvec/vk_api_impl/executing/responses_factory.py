from vk_api.requests_pool import RequestResult
from suvec.common.top_level_types import User
from suvec.common.executing import ResponsesFactory
from .parsers import FriendsParser, GroupsParser
from .response import VkApiResponse


class VkApiResponsesFactory(ResponsesFactory):
    def create_friends_response(self, request_res: RequestResult, user: User):
        return VkApiResponse(request_result=request_res, user=user, parser=FriendsParser())

    def create_groups_response(self, request_res: RequestResult, user: User):
        return VkApiResponse(request_result=request_res, user=user, parser=GroupsParser())
