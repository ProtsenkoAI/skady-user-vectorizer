from ..response import Response
from interfaces import User
from vk_api.requests_pool import RequestResult


class VkApiResponse(Response):
    def __init__(self, request_result: RequestResult, user: User, parser):
        super().__init__(request_result=request_result, user=user, parser=parser)

    def get_response_value(self):
        return self.request_result.result
