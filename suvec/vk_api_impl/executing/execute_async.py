from suvec.common.utils import split
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes

from typing import List

import asyncio
from aiovk.pools import AsyncVkExecuteRequestPool
from python_socks import ProxyConnectionError
from aiohttp import client_exceptions
from ..session.session_units import AioVkSessionUnit


async def execute_async(responses_factory, requests: List[Request], session_unit: AioVkSessionUnit, max_pool_size=25,
                        requests_per_second_limit=3, ) -> List[ParseRes]:
    session = session_unit.get()
    token_session, access_token = session.session, session.access_token

    pool_executes = []
    responses = []
    awaited_requests_and_raw_responses = []

    for idx, requests_batch in enumerate(split(requests, max_pool_size)):
        # creating new pool every time because it cleans list of executed pools only after response,
        #   thus if we use old pool the pool can be accidentally awaited second time
        pool = AsyncVkExecuteRequestPool(token_session_class=token_session, call_number_per_request=25)
        for req in requests_batch:
            resp = pool.add_call(req.get_method(), access_token, method_args=req.get_request_kwargs())
            awaited_requests_and_raw_responses.append((req, resp))

        execute_res_awaitable = pool.execute()
        pool_executes.append(execute_res_awaitable)
        if idx % requests_per_second_limit == 0 and idx != 0:
            try:
                # TODO: refactor this try/except
                resps, met_access_err = await _gather_responses(responses_factory,
                                                                awaited_requests_and_raw_responses,
                                                                pool_executes)

                responses.extend(resps)
                if met_access_err:
                    print("met access error", met_access_err)
                    session_unit.access_error_occurred()
                    session = session_unit.get()
                    token_session, access_tokzen = session.session, session.access_token

            except ProxyConnectionError as e:
                # TODO: maybe should call only with unsuccessful requests, if error can occur
                #  in the middle of execution
                raise e
            if awaited_requests_and_raw_responses:
                # if there are still requests without response (some aio issue,
                # need to investigate), should add them to requests again
                # TODO: refactor
                not_executed_requests, _ = zip(*awaited_requests_and_raw_responses)
                requests.extend(not_executed_requests)
                awaited_requests_and_raw_responses = []

            await asyncio.sleep(1)

    if awaited_requests_and_raw_responses:
        # last iteration
        resps, met_access_err = await _gather_responses(responses_factory,
                                                        awaited_requests_and_raw_responses,
                                                        pool_executes)
        responses.extend(resps)
    return responses


async def _gather_responses(responses_factory, reqs_and_raw_resps, executes):
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
            resp, access_error = responses_factory.create(resp, req)
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
