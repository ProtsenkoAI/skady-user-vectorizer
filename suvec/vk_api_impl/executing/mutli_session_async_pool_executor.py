from typing import List
import asyncio

from suvec.common.requesting import Request
from suvec.common.executing import ParseRes

from .async_pool_executor import AsyncVkApiPoolExecutor


class MultiSessionAsyncVkApiPoolExecutor(AsyncVkApiPoolExecutor):
    """Realisation with support of simultaneous requests from multiple sessions
    """

    def __init__(self, *args, nb_sessions: int = 2, **kwargs):
        self.nb_sessions = nb_sessions
        super().__init__(*args, **kwargs)

    def create_sessions_container(self, session_manager, container):
        # TODO: refactor relations with parent class
        session_manager.allocate_sessions(self.nb_sessions, container)

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        return asyncio.run(self._multi_session_execute(requests))

    async def _multi_session_execute(self, requests: List[Request]) -> List[ParseRes]:
        sessions = self.sessions_container.get()
        requests_parts = self._split(requests, len(sessions))
        execute_results = []

        for part, (session_id, session) in zip(requests_parts, sessions):
            responses = self.execute_async(part, session.access_token, session.session, session_id)
            execute_results.append(responses)

        awaited_execute_results = await asyncio.gather(*execute_results)

        responses = []
        for part in awaited_execute_results:
            responses.extend(part)
        return responses

    @staticmethod
    def _split(lst, nb_splits):
        if len(lst) < nb_splits:
            return [lst]
        step_size = len(lst) // nb_splits
        parts = []
        for start_idx in range(0, len(lst), step_size):
            parts.append(lst[start_idx: start_idx + step_size])
        return parts
