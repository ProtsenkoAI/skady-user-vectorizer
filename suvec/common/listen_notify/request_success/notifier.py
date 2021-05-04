from typing import List

from .listener import RequestSuccessListener
from ...top_level_types import User


class RequestSuccessNotifier:
    def __init__(self):
        self.request_success_listeners: List[RequestSuccessListener] = []

    def register_request_success_listener(self, listener: RequestSuccessListener):
        self.request_success_listeners.append(listener)

    def notify_request_success(self, user: User, req_type: str):
        for listener in self.request_success_listeners:
            listener.request_succeed(user, req_type)
