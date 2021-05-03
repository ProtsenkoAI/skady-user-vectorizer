from .listener import BadPasswordListener


class BadPasswordNotifier:
    def __init__(self):
        self.bad_password_listeners = []

    def notify_bad_password(self):
        for listener in self.bad_password_listeners:
            listener.bad_password()

    def register_bad_password_listener(self, listener: BadPasswordListener):
        self.bad_password_listeners.append(listener)
