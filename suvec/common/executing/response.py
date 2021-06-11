from .parse_res import ParseRes, ErrorObj
from .types import ResponseObj
from suvec.common.top_level_types import User


class Response:
    def __init__(self, request_result, user: User, parser):
        self.request_result = request_result
        self.user = user
        self.parser = parser

    def parse(self) -> ParseRes:
        # TODO: this check is vk_api lib specific. aiovk .error is None by default, need to tackle.
        if self.request_result.error is not False and self.request_result.error is not None:
            resp_obj = ResponseObj(value=self._get_error(), is_error=True)
        else:
            resp_obj = ResponseObj(value=self.get_response_value(), is_error=False)
        return self.parser.parse(resp_obj, user=self.user)

    def get_response_value(self):
        return self.request_result.result

    def _get_error(self) -> ErrorObj:
        return ErrorObj(code=self.request_result.error["error_code"], error=self.request_result.error)
