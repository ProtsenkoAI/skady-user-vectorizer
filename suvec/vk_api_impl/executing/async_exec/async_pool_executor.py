from typing import List, Generator
import asyncio
from aiovk import exceptions
import aiovk
from aiovk import drivers
from aiovk.pools import AsyncVkExecuteRequestPool

from suvec.common.requesting import Request
from suvec.common.executing import Response
from ..pool_executor import VkApiPoolExecutor


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
    def execute(self, requests: List[Request]) -> List[Response]:
        vk_api_pool = self.session_manager.get_session()

        proxy_address = self.session_manager.proxy_address
        proxy_ip, proxy_port = proxy_address.split(":")

        token_session = _TokenSessionWithProxy(proxy_ip, proxy_port)
        access_token = vk_api_pool.vk_session.token["access_token"]

        responses = asyncio.run(self.execute_async(requests, access_token, token_session))
        return responses

    async def execute_async(self, requests: List[Request], access_token: str, token_session: _TokenSessionWithProxy
                            ) -> List[Response]:
        pool_executes = []
        req_and_response_async = []

        pool = AsyncVkExecuteRequestPool(token_session_class=token_session)  # passing wrapper to support proxy
        for idx, requests_batch in enumerate(self._create_batches(requests, self.max_pool_size)):
            print("execute batch idx", idx)
            for req in requests_batch:
                resp = pool.add_call(req.get_method(), access_token, method_args=req.get_request_kwargs())
                req_and_response_async.append((req, resp))

            # TODO: uncomment
            execute_res_awaitable = pool.execute()
            pool_executes.append(execute_res_awaitable)
            if idx % 3 == 2:
                # waiting till last 3 requests end and sleep to fit into requests limit
                try:
                    await asyncio.gather(*pool_executes)
                    pool_executes = []
                    await asyncio.sleep(0.5)  # editable, need experiments
                except exceptions.VkAPIError as e:
                    if e.error_code == 6:
                        print("Rate limit exceeded!")
                        await asyncio.sleep(1)
                    else:
                        raise e

        if pool_executes:
            # awaiting left pools
            await asyncio.gather(*pool_executes)
        # TODO: uncomment
        # await asyncio.gather(*pool_executes)
        responses = [req.create_response(raw_resp_async) for req, raw_resp_async in req_and_response_async]
        return responses

    @staticmethod
    def _create_batches(lst: List[Request], batch_size: int) -> Generator[List[Request], None, None]:
        start_idx = 0
        while start_idx < len(lst):
            yield lst[start_idx: start_idx + batch_size]
            start_idx += batch_size
