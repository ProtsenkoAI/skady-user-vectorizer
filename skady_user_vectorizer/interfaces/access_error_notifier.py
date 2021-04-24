from .access_error_listener import AccessErrorListener
from .top_level_types import User


class AccessErrorNotifier:
    def __init__(self):
        self.listeners = []

    def register_access_error_listener(self, listener: AccessErrorListener):
        self.listeners.append(listener)

    def notify_access_error_listeners(self, user: User, type_of_request: str, *args, **kwargs):
        for listener in self.listeners:
            listener.access_error_occurred(user=user, type_of_request=type_of_request, *args, **kwargs)
