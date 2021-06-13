from typing import List, Callable
from abc import abstractmethod

from ..top_level_types import User
from ..listen_notify import AbstractAccessErrorListener
from .request import Request
from .requests_creator import RequestsCreator
from .requester import Requester


class BaseRequesterImpl(Requester, AbstractAccessErrorListener):
    def __init__(self, request_creator: RequestsCreator, max_requests_per_call: int = 100):
        self.users_to_friends_request = []
        self.users_to_groups_request = []
        self.request_creator = request_creator
        self.max_requests_per_call = max_requests_per_call

    def get_requests(self) -> List[Request]:
        return self.request_friends_and_groups()

    def request_friends_and_groups(self):
        requests = []
        requests += self.create_requests(self.users_to_friends_request, self.request_creator.friends_request,
                                         self.max_requests_per_call)
        # Friends requests is first priority, then go groups requests
        requests_left = self.max_requests_per_call - len(requests)
        requests += self.create_requests(self.users_to_groups_request, self.request_creator.groups_request,
                                         requests_left)
        return requests

    @abstractmethod
    def add_users(self, users: List[User]):
        ...

    def create_requests(self, users: List[User], request_creator_method: Callable, max_requests: int):
        requests = []
        while users:
            requests.append(request_creator_method(users.pop(0)))
            if len(requests) >= max_requests:
                break
        return requests

    def access_error_occurred(self, user, type_of_request: str, *args, **kwargs):
        # TODO: at the moment if access error occurs, we break parsing, thus all users after first one will be dropped
        #   and not moved to request queues again. Solution will be tol listen success parse notification and remove
        #   from list of users needed parsing, but it'll bring overheads. Thus, we don't do it because now there are
        #   too many users to process them all and we don't have problem with absence of users to parse.
        if type_of_request == "friends":
            self.users_to_friends_request.append(user)
        elif type_of_request == "groups":
            self.users_to_groups_request.append(user)
        else:
            raise ValueError(f"Unknown type_of_request: {type_of_request}")
