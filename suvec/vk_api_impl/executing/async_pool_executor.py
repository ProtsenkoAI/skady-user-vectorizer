from typing import List
import asyncio
from aiovk.pools import AsyncVkExecuteRequestPool

from suvec.common.requesting import Request
from suvec.common.utils import split
from suvec.common.executing import ParseRes
from suvec.common.executing.executor import Executor
from ..session.session_manager_impl import SessionManagerImpl
from ..session.sessions_containers import AioVkSessionsContainer, TokenSessionWithProxyMaker
from suvec.common.executing import ResponsesFactory


class AsyncVkApiPoolExecutor(Executor):
    def __init__(self, session_manager: SessionManagerImpl, responses_factory: ResponsesFactory, max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.sessions_container = AioVkSessionsContainer(errors_handler=session_manager.get_errors_handler())
        # TODO: Refactor this place (pass allocated sessions, not session_manager)
        self.fill_sessions_container(session_manager, self.sessions_container)
        self.requests_per_second_limit = 3

    def fill_sessions_container(self, session_manager, container):
        session_manager.allocate_sessions(1, container)

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        session_id, session = self.sessions_container.get()[0]
        responses = asyncio.run(self.execute_async(requests, session.access_token, session.session, session_id))
        return responses

    async def execute_async(self, requests: List[Request], access_token: str, token_session: TokenSessionWithProxyMaker,
                            session_id) -> List[ParseRes]:
        pool_executes = []
        responses = []
        awaited_requests_and_raw_responses = []
        for idx, requests_batch in enumerate(split(requests, self.max_pool_size)):
            # creating new pool every time because it cleans list of executed pools only after response,
            #   thus if we use old pool the pool can be accidentally awaited second time
            pool = AsyncVkExecuteRequestPool(token_session_class=token_session, call_number_per_request=25)
            for req in requests_batch:
                resp = pool.add_call(req.get_method(), access_token, method_args=req.get_request_kwargs())
                awaited_requests_and_raw_responses.append((req, resp))

            execute_res_awaitable = pool.execute()
            pool_executes.append(execute_res_awaitable)
            if idx % self.requests_per_second_limit == 0 and idx != 0:
                responses.extend(await self._gather_responses(awaited_requests_and_raw_responses,
                                                              pool_executes,
                                                              session_id))
                await asyncio.sleep(1)

        if awaited_requests_and_raw_responses:
            # last iteration
            responses.extend(await self._gather_responses(awaited_requests_and_raw_responses,
                                                          pool_executes,
                                                          session_id))
        return responses

    async def _gather_responses(self, reqs_and_raw_resps, executes, session_id):
        """Clears reqs and resps, executes and returns responses"""
        # executes are awaitable objects. When they'll be awaited, responses objects will be filled with data
        responses = []
        try:
            await asyncio.gather(*[executes.pop(0) for _ in range(len(executes))])
            while reqs_and_raw_resps:
                req, resp = reqs_and_raw_resps.pop(0)
                responses.append(self.responses_factory.create(resp, req, session_id))

        except asyncio.TimeoutError:
            print("TimeoutError!")
            pass

        return responses
