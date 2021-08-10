from typing import List
import asyncio
from aiovk.pools import AsyncVkExecuteRequestPool
from python_socks import ProxyConnectionError
from aiohttp import client_exceptions

from suvec.common.requesting import Request
from suvec.common.utils import split
from suvec.common.executing import ParseRes
from suvec.common.executing.executor import Executor
from ..session.session_manager_impl import SessionManagerImpl
from ..session.sessions_containers import AioVkSessionsContainer
from ..errors_handler import VkApiErrorsHandler
from suvec.common.executing import ResponsesFactory


class AsyncVkApiPoolExecutor(Executor):
    # TODO: if caught access error, need to stop requesting (for the errored requests type) and change requests to
    #   not-banned type or change session

    # TODO: better sessions interface to replace - object passed to execute_async which you can call replace()
    #   and proxy/credentials will be replaced, without boilerplate with self.sessions_container

    def __init__(self, session_manager: SessionManagerImpl, responses_factory: ResponsesFactory,
                 errors_handler: VkApiErrorsHandler, max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.sessions_container = AioVkSessionsContainer(errors_handler=session_manager.get_errors_handler(),
                                                         session_manager=session_manager)
        self.errors_handler = errors_handler
        # TODO: Refactor this place (pass allocated sessions, not session_manager)
        self.fill_sessions_container(session_manager, self.sessions_container)
        self.requests_per_second_limit = 3

    def fill_sessions_container(self, session_manager, container):
        session_manager.allocate_sessions(1, container)

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        session_id = self.sessions_container.get()[0][0]
        responses = asyncio.run(self.execute_async(requests, session_id))
        return responses

    async def execute_async(self, requests: List[Request], session_id) -> List[ParseRes]:
        session = dict(self.sessions_container.get())[session_id]
        token_session, access_token = session.session, session.access_token

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
                try:
                    # TODO: refactor this try/except
                    resps, met_access_err = await self._gather_responses(awaited_requests_and_raw_responses,
                                                                         pool_executes,
                                                                         session_id)

                    responses.extend(resps)
                    if met_access_err:
                        print("met access error", met_access_err)
                        resp = self.sessions_container.replace(session_id)
                        print("resp", resp)
                        if resp is not None:
                            # returns None if have no resources
                            session_id, session = resp
                            token_session, access_tokzen = session.session, session.access_token

                except ProxyConnectionError:
                    # TODO: maybe should call only with unsuccessful requests, if error can occur
                    #  in the middle of execution
                    self.errors_handler.proxy_error(requests, session_id)
                if awaited_requests_and_raw_responses:
                    # if there are still requests without response (some aio issue,
                    # need to investigate), should add them to requests again
                    # TODO: refactor
                    requests.extend([req for req, resp in awaited_requests_and_raw_responses])
                    awaited_requests_and_raw_responses = []

                await asyncio.sleep(1)

        if awaited_requests_and_raw_responses:
            # last iteration
            resps, met_access_err = await self._gather_responses(awaited_requests_and_raw_responses,
                                                                 pool_executes,
                                                                 session_id)
            responses.extend(resps)
        return responses

    async def _gather_responses(self, reqs_and_raw_resps, executes, session_id):
        """Clears reqs and resps, executes and returns responses"""
        # executes are awaitable objects. When they'll be awaited, responses objects will be filled with data
        responses = []
        met_access_error = False
        try:
            await asyncio.gather(*[executes.pop(0) for _ in range(len(executes))])
            # TODO: need to try to extract responses whose execute() didn't raised errors
            while reqs_and_raw_resps:
                req, resp = reqs_and_raw_resps.pop(0)
                # TODO: don't need folded responses factory inside executor (bad design + not async),
                #   need to move it to CrawlRunner loop
                resp, access_error = self.responses_factory.create(resp, req, session_id)
                met_access_error = met_access_error or access_error
                responses.append(resp)

        except asyncio.TimeoutError:
            print("TimeoutError!")
            pass
        except client_exceptions.ContentTypeError as e:
            # TODO: log, process in proper way
            print("Content Type Error:", e)
            pass

        return responses, met_access_error
