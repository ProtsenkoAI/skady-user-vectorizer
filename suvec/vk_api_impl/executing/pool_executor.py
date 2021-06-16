from typing import List
from vk_api import VkRequestsPool

from ..session.session_manager_impl import SessionManagerImpl
from ..session.sessions_containers import VkApiSessionsContainer
from suvec.common.executing import ResponsesFactory
from suvec.common.requesting import Request
from suvec.common.executing import ParseRes
from suvec.common.executing.executor import Executor


class VkApiPoolExecutor(Executor):
    # TODO: this component isn't being used now, but it has no unittests, thus it starts to rot.
    def __init__(self, session_manager: SessionManagerImpl, responses_factory: ResponsesFactory, max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.responses_factory = responses_factory
        self.sessions_container = VkApiSessionsContainer(errors_handler=session_manager.get_errors_handler())
        session_manager.allocate_sessions(1, self.sessions_container)

    def execute(self, requests: List[Request]) -> List[ParseRes]:
        # TODO: need fast check for access error and other errors when should break executing.
        #   Otherwise have large overheads
        session_id, session = self.sessions_container.get()[0]
        not_executed_requests = []
        for idx, req in enumerate(requests):
            resp_raw = session.method(req.get_method(), values=req.get_request_kwargs())
            not_executed_requests.append((req, resp_raw))
            self._execute_pool_if_needed(session, idx)

        self._execute(session)
        responses = [self.responses_factory.create(req_res, request, session_id)
                     for request, req_res in not_executed_requests]
        return responses

    def _execute_pool_if_needed(self, session: VkRequestsPool, idx: int):
        if (idx + 1) % self.max_pool_size == 0:
            self._execute(session)

    def _execute(self, session):
        # TODO: handle this error, that can occur: RemoteDisconnected('Remote end closed connection without response')
        # TODO: handle JSONDecodeError: Expecting value: line 1 column 247645 (char 247644)
        session.execute()

