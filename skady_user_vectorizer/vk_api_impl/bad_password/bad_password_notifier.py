from .bad_password_listener import BadPasswordListener


class BadPasswordNotifier:
    def __init__(self):
        self.listeners = []

    def notify_bad_password(self):
        for listener in self.listeners:
            listener.bad_password()

    def register_bad_password_listener(self, listener: BadPasswordListener):
        self.listeners.append(listener)
