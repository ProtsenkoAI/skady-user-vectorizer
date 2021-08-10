from typing import List
import asyncio
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common.executing.executor import Executor
from suvec.common.executing import ResponsesFactory
from .execute_async import execute_async
from ..session.session_units import AioVkSessionUnit


class AsyncVkApiPoolExecutor(Executor):
    def __init__(self,
                 responses_factory: ResponsesFactory,
                 session_unit: AioVkSessionUnit,
                 max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.ses_unit = session_unit
        self.requests_per_second_limit = 3

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        responses = asyncio.run(execute_async(self.responses_factory, requests, self.ses_unit, self.max_pool_size,
                                              self.requests_per_second_limit))
        return responses
