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
    # TODO: refactor
    def __init__(self, session_manager: SessionManagerImpl, responses_factory: ResponsesFactory, max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.sessions_container = AioVkSessionsContainer(errors_handler=session_manager.get_errors_handler())
        # TODO: Refactor this place (pass allocated sessions, not session_manager)
        self.create_sessions_container(session_manager, self.sessions_container)

    def create_sessions_container(self, session_manager, container):
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
            if idx % 3 == 2:
                # waiting till last 3 requests end and sleep to fit into requests limit
                try:
                    await asyncio.gather(*pool_executes)
                    responses.extend(self._create_responses(awaited_requests_and_raw_responses, session_id))
                    # TODO: can increase speed if will reduce sleep time, catch speed limits and re-send failed requests
                    await asyncio.sleep(1)
                except asyncio.TimeoutError:
                    print("TimeoutError!")
                    pass
                finally:
                    awaited_requests_and_raw_responses = []
                    pool_executes = []

        if pool_executes:
            await asyncio.gather(*pool_executes)  # awaiting left pools
            responses.extend(self._create_responses(awaited_requests_and_raw_responses, session_id))
        return responses

    def _create_responses(self, awaited_reqs_and_resps, session_id):
        return [self.responses_factory.create(resp, req, session_id) for req, resp in awaited_reqs_and_resps]
