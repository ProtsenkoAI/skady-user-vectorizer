from typing import List

from .listener import SessionLimitListener


class SessionLimitNotifier:
    def __init__(self):
        self.listeners: List[SessionLimitListener] = []

    def register_session_limit_notifier(self, listener: SessionLimitListener):
        self.listeners.append(listener)

    def notify_session_limit(self):
        for listener in self.listeners:
            listener.session_limit()
