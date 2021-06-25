from typing import List, Tuple

from .listener import SessionErrorListener


class SessionErrorNotifier:
    def __init__(self):
        self.session_error_listeners: List[SessionErrorListener] = []

    def register_session_error_listener(self, listener: SessionErrorListener):
        self.session_error_listeners.append(listener)

    def notify_session_error(self, session_id: int):
        for listener in self.session_error_listeners:
            listener.session_error_occurred(session_id)

    def notify_bad_password(self, session_id: int):
        for listener in self.session_error_listeners:
            listener.bad_password(session_id)

    def notify_proxy_error(self, session_id: int):
        for listener in self.session_error_listeners:
            listener.proxy_error_occurred(session_id)
