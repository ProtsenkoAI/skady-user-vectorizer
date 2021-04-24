from abc import ABC, abstractmethod
from vk_api.requests_pool import RequestResult

from .parse_res import FriendsParseRes, GroupsParseRes, ParseRes, VkApiErrorObj, ResponseObj
from interfaces import Parser, User


class Response(ABC):
    def __init__(self, request_result: RequestResult, user: User):
        self.request_result = request_result
        self.user = user

    @abstractmethod
    def parse(self, parser: Parser) -> ParseRes:
        ...

    def check_error_occurred(self):
        return self.request_result.error is not False

    def get_error(self) -> VkApiErrorObj:
        return VkApiErrorObj(code=self.request_result.error.response.status_code, error=self.request_result.error)


class FriendsResponse(Response):
    def parse(self, parser: Parser) -> FriendsParseRes:
        if self.check_error_occurred():
            return parser.parse_friends(ResponseObj(value=self.get_error(), is_error=True), user=self.user)
        return parser.parse_friends(ResponseObj(value=self.request_result.result, is_error=True), user=self.user)


class GroupsResponse(Response):
    def parse(self, parser: Parser) -> GroupsParseRes:
        if self.check_error_occurred():
            return parser.parse_friends(ResponseObj(value=self.get_error(), is_error=True), user=self.user)
        return parser.parse_groups(ResponseObj(value=self.request_result.result, is_error=True), user=self.user)
