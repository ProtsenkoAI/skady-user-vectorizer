from suvec.common.postproc import ParsedProcessor
from suvec.common.executing import ParseRes
from suvec.common.listen_notify import SessionLimitNotifier


class SessionSwitchingParsedProcessor(ParsedProcessor, SessionLimitNotifier):
    """Wrapper that adds tracking of requests number per session and notifies when limit of requests
    is reached
    """
    def __init__(self, *args, requests_per_session_limit: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_requests_cnt = 0
        self.req_limit = requests_per_session_limit

    def process(self, parsed_results: ParseRes, *args, **kwargs):
        self.session_requests_cnt += 1
        super().process(parsed_results)
        if self.session_requests_cnt >= self.req_limit:
            self.notify_session_limit()
            self.session_requests_cnt = 0
