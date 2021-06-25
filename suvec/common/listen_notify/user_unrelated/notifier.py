from typing import List

from .listener import UserUnrelatedErrorListener
from ...requesting import Request


class UserUnrelatedErrorNotifier:
    def __init__(self):
        self.user_unrelated_listeners: List[UserUnrelatedErrorListener] = []

    def register_user_unrelated_listener(self, listener: UserUnrelatedErrorListener):
        self.user_unrelated_listeners.append(listener)

    def notify_user_unrelated_error(self, request: Request):
        for listener in self.user_unrelated_listeners:
            listener.user_unrelated_error(request)
