from abc import ABC, abstractmethod

from ..listen_notify import RequestSuccessNotifier, SessionLimitNotifier
from .parsed_processor import ParseRes


class ProcessorProcessHook(ABC):
    @abstractmethod
    def process(self, res: ParseRes):
        ...


class ProcessorProcessSuccessHook(ABC):
    @abstractmethod
    def process_success(self, res: ParseRes):
        ...


class ProcessHookLimitSessionRequests(ProcessorProcessHook, SessionLimitNotifier):
    def __init__(self, req_limit: int = 50000):
        super().__init__()
        self.session_requests_cnt = 0
        self.req_limit = req_limit

    def process(self, res: ParseRes):
        self.session_requests_cnt += 1
        if self.session_requests_cnt >= self.req_limit:
            self.notify_session_limit()
            self.session_requests_cnt = 0


class ProcessHookSuccessParseNotifier(ProcessorProcessSuccessHook, RequestSuccessNotifier):
    def process_success(self, res: ParseRes):
        self.notify_request_success(res.user, res.request_type)
