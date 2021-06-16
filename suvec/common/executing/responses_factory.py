from abc import ABC, abstractmethod
from .types import RequestResult
from ..requesting import Request
from . import ParseRes


class ResponsesFactory(ABC):
    def create(self, req_res: RequestResult, req: Request, session_data) -> ParseRes:
        if req.req_type == "friends":
            return self.create_friends_response(req_res, req, session_id=session_data)
        elif req.req_type == "groups":
            return self.create_groups_response(req_res, req, session_id=session_data)
        else:
            raise ValueError(f"Invalid req_type: {req.req_type}")

    @abstractmethod
    def create_friends_response(self, request_res: RequestResult, req: Request, session_id):
        ...

    @abstractmethod
    def create_groups_response(self, request_res: RequestResult, req: Request, session_id):
        ...
