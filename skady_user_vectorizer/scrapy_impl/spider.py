import scrapy
from scrapy.http import Response

from interfaces import Requester, User


class Spider(scrapy.spiders.CrawlSpider):
    name = "Skady users spider"

    def __init__(self, requester: Requester, start_user: User, *args, **kwargs):
        self.requester = requester
        self.start_user = start_user
        super().__init__(*args, **kwargs)

    def start_requests(self):
        self.requester.add_users([self.start_user])
        yield from self.requester.get_requests()

    def parse(self, response: Response, **kwargs):
        raise NotImplementedError("This spider should delegate all parsing to requester parser")
