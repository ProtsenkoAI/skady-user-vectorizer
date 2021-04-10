from ..interfaces import UsersStorage
from global_types import User, Users

import requests
import scrapy
from scrapy.responsetypes import Response
from scrapy import Request
# from scrapy.spiders.init import InitSpider
from scrapy.spiders import CrawlSpider
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest

from time import time, sleep


class ScrapyVkSpider(CrawlSpider):
    # TODO: encapsulate authorization to separate object
    def __init__(self, storage: UsersStorage, start_user: User, users_needed: int = 1000):
        self.storage = storage
        self.users_needed = users_needed
        self.start_url = start_user.url
        self.vk_login_page_url = "https://login.vk.com/?act=login"
        super().__init__(name="scrapy_vk_spider")
        self.cookies = {}
        self.is_authorized = False

    def start_requests(self):
        # print(self.crawler.engine.schedule(self.init_request(), self))
        yield self.init_request()
        # sleep(3)
        # yield Request(url=self.start_url, callback=self.parse)

    def init_request(self):
        return Request(url=self.vk_login_page_url, callback=self.login_and_schedule_start_requests)

    def login_and_schedule_start_requests(self, log_in_page_resp):
        yield self.login_and_start_parsing(log_in_page_resp)

    def login_and_start_parsing(self, response):
        form_request = FormRequest.from_response(response,
                                                 formid="login_form",
                                                 formdata={"email": "79600988916",
                                                           "pass": 'bQ30BIcK'},
                                                 callback=self.check_login_and_start_crawling,
                                                 cookies=self.cookies)
        return form_request

    def check_login_and_start_crawling(self, login_result_resp):
        self.check_login_response(login_result_resp)
        yield Request(url=self.start_url, callback=self.parse)

    def check_login_response(self, response):
        print("time obtaining login response", time())
        print("login failed:", "Login failed." in response.text)
        print("login response", response.url)
        print("Cookies list:", response.headers.getlist("Set-Cookie"))
        # an example request to page to check that authorized successfully

    def parse(self, response, **kwargs):
        print("Yay we parsing someone")
        print("time parsing", time())
        are_friends_open = self._check_friends_open(response)
        if are_friends_open:
            friends = self._get_friends(response)
            self.storage.extend(friends)
            for friend in friends:
                yield Request(friend.url, self.parse)

            self._stop_if_needed()  # TODO: move to another part

    def _check_friends_open(self, response: Response) -> bool:
        print("Check friends open")
        print("User page", response.url)
        print("Not authorized", "You have to sign in" in response.text)
        return False

    def _get_friends(self, response: Response) -> Users:
        raise NotImplementedError

    def _stop_if_needed(self):
        if len(self.storage) >= self.users_needed:
            raise CloseSpider("Enough is enough")
