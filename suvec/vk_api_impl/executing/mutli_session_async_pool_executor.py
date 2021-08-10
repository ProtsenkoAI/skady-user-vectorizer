from typing import List
import asyncio

from .execute_async import execute_async
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common.executing import ResponsesFactory
from suvec.common import utils
from ..session.session_units import AioVkSessionUnit

from suvec.common.executing.executor import Executor


class MultiSessionAsyncVkApiPoolExecutor(Executor):
    """Realisation with support of simultaneous requests from multiple sessions
    """

    def __init__(self,
                 responses_factory: ResponsesFactory,
                 session_manager,
                 nb_sessions=2,
                 max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.ses_units = [AioVkSessionUnit(session_manager) for _ in range(nb_sessions)]
        self.responses_factory = responses_factory
        # TODO: Refactor this place (pass allocated sessions, not session_manager)
        self.requests_per_second_limit = 3

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        return asyncio.run(self._multi_session_execute(requests))

    async def _multi_session_execute(self, requests: List[Request]) -> List[ParseRes]:
        # TODO: refactor working with idxs and sessions objects
        requests_parts = utils.split(requests, parts=len(self.ses_units))
        execute_results = []
        for part, ses_unit in zip(requests_parts, self.ses_units):
            responses = execute_async(self.responses_factory, part, ses_unit, self.max_pool_size,
                                      self.requests_per_second_limit)
            execute_results.append(responses)

        awaited_execute_results = await asyncio.gather(*execute_results)
        responses = []
        for part in awaited_execute_results:
            responses.extend(part)
        return responses
