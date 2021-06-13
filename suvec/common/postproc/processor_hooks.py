from abc import ABC, abstractmethod

from ..listen_notify import RequestSuccessNotifier
from .parsed_processor import ParseRes


class ProcessorSuccessHook(ABC):
    @abstractmethod
    def process_success(self, res: ParseRes):
        ...


class HookSuccessParseNotifier(ProcessorSuccessHook, RequestSuccessNotifier):
    def process_success(self, res: ParseRes):
        self.notify_request_success(res.request.user, res.request.req_type)
