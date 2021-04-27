from common.executing import Response
from common.top_level_types import User
from vk_api.requests_pool import RequestResult


class VkApiResponse(Response):
    def __init__(self, request_result: RequestResult, user: User, parser):
        super().__init__(request_result=request_result, user=user, parser=parser)

    def get_response_value(self):
        return self.request_result.result