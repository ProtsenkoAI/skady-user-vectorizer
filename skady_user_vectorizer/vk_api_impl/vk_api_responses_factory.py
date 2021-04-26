from vk_api.requests_pool import RequestResult
from interfaces import User
from .vk_api_specific.vk_api_parsers import FriendsParser, GroupsParser
from .vk_api_specific.vk_api_response import VkApiResponse


class VkApiResponsesFactory:
    # TODO: create interface and move to interfaces

    def create_friends_response(self, request_res: RequestResult, user: User):
        return VkApiResponse(request_result=request_res, user=user, parser=FriendsParser())

    def create_groups_response(self, request_res: RequestResult, user: User):
        return VkApiResponse(request_result=request_res, user=user, parser=GroupsParser())
