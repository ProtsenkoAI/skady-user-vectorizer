from scrapy.http import Response

from interfaces import Parser, FriendsParseRes, GroupsParseRes


class ScrapyParser(Parser):
    def parse_friends(self, response: Response) -> FriendsParseRes:
        print("friends response", response.text)
        raise NotImplementedError

    def parse_groups(self, response: Response) -> GroupsParseRes:
        print("groups response", response.text)
        raise NotImplementedError

    def check_auth_success(self, response: Response) -> bool:
        return response.url == "https://m.vk.com/feed"
