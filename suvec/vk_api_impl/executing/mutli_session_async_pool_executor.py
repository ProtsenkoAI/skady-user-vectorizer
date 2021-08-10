from typing import List
import asyncio

from .execute_async import execute_async
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common.executing import ResponsesFactory
from suvec.common import utils
from ..session.session_units import AioVkSessionUnit

from suvec.common.executing.executor import Executor
from ..session.session_manager_impl import OutOfRecords


class MultiSessionAsyncVkApiPoolExecutor(Executor):
    """Realisation with support of simultaneous requests from multiple sessions
    """

    def __init__(self,
                 responses_factory: ResponsesFactory,
                 session_units: List[AioVkSessionUnit],
                 max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.ses_units = session_units
        self.responses_factory = responses_factory
        self.requests_per_second_limit = 3

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        return asyncio.run(self._multi_session_execute(requests))

    async def _multi_session_execute(self, requests: List[Request]) -> List[ParseRes]:
        requests_parts = utils.split(requests, parts=len(self.ses_units))
        execute_results = []

        while requests_parts:  # filling with requests that were failed by some sessions
            new_requests_parts = []
            for idx, part, ses_unit in enumerate(zip(requests_parts, self.ses_units)):
                try:
                    responses = execute_async(self.responses_factory, part, ses_unit, self.max_pool_size,
                                              self.requests_per_second_limit)
                except OutOfRecords:
                    self.ses_units.pop(idx)
                    if len(self.ses_units) == 0:
                        raise OutOfRecords
                    new_requests_parts.append(part)
                else:
                    execute_results.append(responses)

            requests_parts = new_requests_parts

        awaited_execute_results = await asyncio.gather(*execute_results)
        responses = []
        for part in awaited_execute_results:
            responses.extend(part)
        return responses
