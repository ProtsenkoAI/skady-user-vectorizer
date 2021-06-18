from typing import List, Tuple

from .listener import AccessErrorListener


class AccessErrorNotifier:
    def __init__(self):
        self.access_error_listeners: List[Tuple[AccessErrorListener, bool]] = []

    def register_access_error_listener(self, listener: AccessErrorListener, only_request=True):
        self.access_error_listeners.append((listener, only_request))

    def notify_access_error_listeners(self, parse_res):
        # TODO: need other mechanism to notify about access error with different interfaces, because storing
        #   only_request flag leads to changes in notifier
        for listener, only_request in self.access_error_listeners:
            if only_request:
                listener.access_error_occurred(parse_res.request)
            else:
                listener.access_error_occurred(parse_res)
