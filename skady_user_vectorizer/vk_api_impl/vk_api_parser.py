from interfaces import Parser, FriendsParseRes, GroupsParseRes
from .responses import Response
from .parse_res import ParseRes, FriendsParseRes, GroupsParseRes


class VkApiParser:
    # TODO: union with parser from interfaces
    def parse(self, response: Response) -> ParseRes:
        raise NotImplementedError
