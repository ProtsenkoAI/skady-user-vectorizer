from typing import List
import asyncio
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common.executing.executor import Executor
from suvec.common.executing import ResponsesFactory
from .execute_async import execute_async
from ..session.session_units import AioVkSessionUnit


class AsyncVkApiPoolExecutor(Executor):
    # TODO: if caught access error, need to stop requesting (for the errored requests type) and change requests to
    #   not-banned type or change session

    # TODO: better sessions interface to replace - object passed to execute_async which you can call replace()
    #   and proxy/credentials will be replaced, without boilerplate with self.sessions_container

    def __init__(self,
                 responses_factory: ResponsesFactory,
                 session_manager,
                 max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.ses_unit = AioVkSessionUnit(session_manager)
        # TODO: Refactor this place (pass allocated sessions, not session_manager)
        self.requests_per_second_limit = 3

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        responses = asyncio.run(execute_async(self.responses_factory, requests, self.ses_unit, self.max_pool_size,
                                              self.requests_per_second_limit))
        return responses
