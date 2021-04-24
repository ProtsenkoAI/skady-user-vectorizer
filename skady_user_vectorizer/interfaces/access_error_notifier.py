from .access_error_listener import AccessErrorListener


class AccessErrorNotifier:
    def __init__(self):
        self.listeners = []

    def register_access_error_listener(self, listener: AccessErrorListener):
        self.listeners.append(listener)

    def notify_access_error_listeners(self):
        for listener in self.listeners:
            listener.access_error_occurred()
