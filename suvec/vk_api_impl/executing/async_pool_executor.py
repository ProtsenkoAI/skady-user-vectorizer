from typing import List, Generator, Tuple
import asyncio
import aiovk
from vk_api.requests_pool import VkRequestsPool
from aiovk import drivers
from aiovk.pools import AsyncVkExecuteRequestPool

from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.vk_api_impl.executing.pool_executor import VkApiPoolExecutor


class _TokenSessionWithProxy:
    """wrapper for AsyncVkExecuteRequestPool from aiovk because it doesn't support passing
    Driver to session"""

    def __init__(self, proxy_ip, proxy_port):
        self.proxy_ip, self.proxy_port = proxy_ip, proxy_port

    def __call__(self, token):
        proxy_driver = drivers.ProxyDriver(self.proxy_ip, self.proxy_port)
        return aiovk.TokenSession(token, driver=proxy_driver)


class AsyncVkApiPoolExecutor(VkApiPoolExecutor):
    # TODO: try to tackle creating a lot of sessions/pools/proxy objects overheads
    # TODO: refactor
    def execute(self, requests: List[Request]) -> List[ParseRes]:
        vk_api_pool, session_id = self.session_manager.get_next_session()
        print("pool", vk_api_pool, "session_id", session_id)
        access_token, token_session = self.prepare_session(vk_api_pool)

        responses = asyncio.run(self.execute_async(requests, access_token, token_session, session_id))
        return responses

    def prepare_session(self, vk_pool: VkRequestsPool) -> Tuple[str, _TokenSessionWithProxy]:
        proxy_ip, proxy_port = self.extract_proxy(vk_pool)
        token_session = _TokenSessionWithProxy(proxy_ip, proxy_port)
        access_token = vk_pool.vk_session.token["access_token"]
        return access_token, token_session

    def extract_proxy(self, vk_api_pool: VkRequestsPool) -> Tuple[str, str]:
        requests_session = vk_api_pool.vk_session.http
        proxy = requests_session.proxies["http"]
        return proxy.split(":")

    async def execute_async(self, requests: List[Request], access_token: str, token_session: _TokenSessionWithProxy,
                            session_id
                            ) -> List[ParseRes]:
        pool_executes = []
        responses = []
        awaited_requests_and_raw_responses = []
        for idx, requests_batch in enumerate(self._create_batches(requests, self.max_pool_size)):
            # creating wrapper to support proxy
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

    @staticmethod
    def _create_batches(lst: List[Request], batch_size: int) -> Generator[List[Request], None, None]:
        start_idx = 0
        while start_idx < len(lst):
            yield lst[start_idx: start_idx + batch_size]
            start_idx += batch_size


class MultiSessionAsyncVkApiPoolExecutor(AsyncVkApiPoolExecutor):
    """Realisation with support of simultaneous requests from multiple sessions
    """

    def __init__(self, *args, nb_sessions: int = 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.nb_sessions = nb_sessions

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        return asyncio.run(self._multi_session_execute(requests))

    async def _multi_session_execute(self, requests: List[Request]) -> List[ParseRes]:
        sessions_and_ids = self.session_manager.get_n_sessions(self.nb_sessions)
        if len(sessions_and_ids) < self.nb_sessions:
            print("Currect number of session is", len(sessions_and_ids), "but need:", self.nb_sessions)
        requests_parts = self._split(requests, len(sessions_and_ids))
        execute_results = []

        for part, (session, session_id) in zip(requests_parts, sessions_and_ids):
            access_token, token_session = self.prepare_session(session)
            responses = self.execute_async(part, access_token, token_session, session_id)
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
