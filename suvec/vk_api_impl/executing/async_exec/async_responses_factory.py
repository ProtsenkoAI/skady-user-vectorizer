from aiovk.pools import AsyncResult
from suvec.common.top_level_types import User
from suvec.common.executing import ResponsesFactory
from ..parsers import FriendsParser, GroupsParser
from .async_response import VkAsyncResponse


class VkAsyncResponsesFactory(ResponsesFactory):
    def create_friends_response(self, request_res: AsyncResult, user: User):
        return VkAsyncResponse(request_result=request_res, user=user, parser=FriendsParser())

    def create_groups_response(self, request_res: AsyncResult, user: User):
        return VkAsyncResponse(request_result=request_res, user=user, parser=GroupsParser())
