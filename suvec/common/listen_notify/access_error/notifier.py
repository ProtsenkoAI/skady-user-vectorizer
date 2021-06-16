from typing import List

from .listener import AccessErrorListener


class AccessErrorNotifier:
    def __init__(self):
        self.access_error_listeners: List[AccessErrorListener] = []

    def register_access_error_listener(self, listener: AccessErrorListener):
        self.access_error_listeners.append(listener)

    def notify_access_error_listeners(self, request):
        for listener in self.access_error_listeners:
            listener.access_error_occurred(request)
