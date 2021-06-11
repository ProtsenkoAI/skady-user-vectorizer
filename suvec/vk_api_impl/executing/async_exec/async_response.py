from suvec.common.executing import Response
from suvec.common.top_level_types import User
from aiovk.pools import AsyncResult


class VkAsyncResponse(Response):
    """aiovk-specific response obj"""
    def __init__(self, request_result: AsyncResult, user: User, parser):
        super().__init__(request_result=request_result, user=user, parser=parser)
