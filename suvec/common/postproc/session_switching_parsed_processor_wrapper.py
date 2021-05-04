from typing import Any

from .parsed_processor_impl import ParsedProcessorImpl
from ..executing import ParseRes
from ..listen_notify import SessionLimitNotifier
from .parsed_processor import ParsedProcessor


def never_used_method(method):
    """Used when adding methods only for type checking, probably because they can't check methods in
        case of __getattribute__ magic"""
    def wrapped(*args, **kwargs) -> Any:
        raise RuntimeError("This method can't be called in this class")
    return wrapped


class SessionSwitchingParsedProcessorWrapper(SessionLimitNotifier, ParsedProcessor):
    """Wrapper that adds tracking of requests number per session and notifies when limit of requests
    is reached
    """
    def __init__(self, parsed_processor: ParsedProcessorImpl, requests_per_session_limit: int):
        super().__init__()
        self.processor = parsed_processor
        self.req_limit = requests_per_session_limit
        self.session_requests_cnt = 0

    def process(self, parsed_results: ParseRes, *args, **kwargs):
        self.session_requests_cnt += 1
        self.processor.process(parsed_results, *args, **kwargs)
        if self.session_requests_cnt >= self.req_limit:
            self.notify_session_limit()
            self.session_requests_cnt = 0

    def __getattribute__(self, item: str):
        """Implements only process method, any other goes to processor attribute"""
        if item in ["process", "session_requests_cnt", "req_limit", "processor"]:
            return object.__getattribute__(self, item)
        else:
            # processor = object.__getattribute__(self, "processor")
            # return processor.__getattribute__(item)
            return self.processor.__getattribute__(item)

    @never_used_method
    def process_success(self, res: ParseRes):
        ...

    @never_used_method
    def get_new_parse_candidates(self):
        ...
