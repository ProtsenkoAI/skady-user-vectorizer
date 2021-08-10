from typing import List
import asyncio

from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common import utils

from .async_pool_executor import AsyncVkApiPoolExecutor


class MultiSessionAsyncVkApiPoolExecutor(AsyncVkApiPoolExecutor):
    """Realisation with support of simultaneous requests from multiple sessions
    """

    def __init__(self, *args, nb_sessions: int = 2, **kwargs):
        self.nb_sessions = nb_sessions
        super().__init__(*args, **kwargs)

    def fill_sessions_container(self, session_manager, container):
        session_manager.allocate_sessions(self.nb_sessions, container)

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        return asyncio.run(self._multi_session_execute(requests))

    async def _multi_session_execute(self, requests: List[Request]) -> List[ParseRes]:
        # TODO: refactor working with idxs and sessions objects
        sessions_items = self.sessions_container.get()
        sessions_ids, _ = zip(*sessions_items)
        requests_parts = utils.split(requests, parts=len(sessions_ids))
        execute_results = []
        for part, session_id in zip(requests_parts, sessions_ids):
            responses = self.execute_async(part, session_id)
            execute_results.append(responses)

        awaited_execute_results = await asyncio.gather(*execute_results)
        responses = []
        for part in awaited_execute_results:
            responses.extend(part)
        return responses
