from abc import ABC, abstractmethod

from .parse_res import ParseRes, ErrorObj
from .types import ResponseObj
from suvec.common.top_level_types import User


class Response(ABC):
    def __init__(self, request_result, user: User, parser):
        self.request_result = request_result
        self.user = user
        self.parser = parser

    def parse(self) -> ParseRes:
        if self.request_result.error is not False:
            resp_obj = ResponseObj(value=self._get_error(), is_error=True)
        else:
            resp_obj = ResponseObj(value=self.get_response_value(), is_error=False)
        return self.parser.parse(resp_obj, user=self.user)

    @abstractmethod
    def get_response_value(self):
        ...

    def _get_error(self) -> ErrorObj:
        # TODO: probably vk-specfic too, thus should make abstractmethod and move to inherited classes
        return ErrorObj(code=self.request_result.error["error_code"], error=self.request_result.error)
