from typing import List

from .listener import SessionLimitListener


class SessionLimitNotifier:
    def __init__(self):
        self.session_limit_listeners: List[SessionLimitListener] = []

    def register_session_limit_listener(self, listener: SessionLimitListener):
        self.session_limit_listeners.append(listener)

    def notify_session_limit(self):
        for listener in self.session_limit_listeners:
            listener.session_limit()
