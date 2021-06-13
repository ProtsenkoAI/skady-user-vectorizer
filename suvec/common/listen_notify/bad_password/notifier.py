from .listener import BadPasswordListener


class BadPasswordNotifier:
    def __init__(self):
        self.bad_password_listeners = []

    def notify_bad_password(self, session_id):
        for listener in self.bad_password_listeners:
            listener.bad_password(session_id)

    def register_bad_password_listener(self, listener: BadPasswordListener):
        self.bad_password_listeners.append(listener)
