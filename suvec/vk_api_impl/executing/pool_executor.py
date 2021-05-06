from typing import List
from vk_api import VkRequestsPool

from ..session.session_manager import SessionManager
from suvec.common.requesting import Request
from suvec.common.executing import Response
from suvec.common.listen_notify import AccessErrorListener


class VkApiPoolExecutor(AccessErrorListener):
    # TODO: later, if vk will raise speed limit errors, need to throttle requests / manage delays
    def __init__(self, session_manager: SessionManager, max_pool_size=25):
        self.max_pool_size = max_pool_size
        self.session_manager = session_manager

    def execute(self, requests: List[Request]) -> List[Response]:
        # TODO: need fast check for access error and other errors when should break executing.
        #   Otherwise have large overheads
        session = self.session_manager.get_session()
        responses = []
        for idx, req in enumerate(requests):
            resp_raw = session.method(req.get_method(), values=req.get_request_kwargs())
            responses.append(req.create_response(resp_raw))
            self._execute_pool_if_needed(session, idx)

        self._execute(session)
        return responses

    def _execute_pool_if_needed(self, session: VkRequestsPool, idx: int):
        if (idx + 1) % self.max_pool_size == 0:
            self._execute(session)

    def _execute(self, session):
        # TODO: handle this error, that can occur: RemoteDisconnected('Remote end closed connection without response')
        # TODO: handle JSONDecodeError: Expecting value: line 1 column 247645 (char 247644)
        session.execute()

    def access_error_occurred(self, *args, **kwargs):
        self.session_manager.reset_session_access_error()
