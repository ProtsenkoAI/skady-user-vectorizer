from suvec.common.executing import Response
from suvec.common.top_level_types import User
from vk_api.requests_pool import RequestResult


class VkApiResponse(Response):
    def __init__(self, request_result: RequestResult, user: User, parser):
        super().__init__(request_result=request_result, user=user, parser=parser)
