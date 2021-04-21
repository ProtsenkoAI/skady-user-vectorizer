from ..interfaces import UsersStorage
from global_types import User, Users

import scrapy
from scrapy.responsetypes import Response
from scrapy import Request
from scrapy.spiders import CrawlSpider
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest
from typing import Optional


class ScrapyVkSpider(CrawlSpider):
    # TODO: catch situations when vk block us because of too frequent requests and log them
    # TODO: add sleep time between requests to prevent blocking
    # TODO: encapsulate authorization to separate object
    def __init__(self, storage: UsersStorage, start_user: User, users_needed: int = 1000,
                 nb_processed_friends: Optional[int] = None):
        self.storage = storage
        self.users_needed = users_needed
        self.start_url = start_user.url
        self.vk_login_page_url = "https://login.vk.com/?act=login"
        self.nb_processed_friends = nb_processed_friends
        super().__init__(name="scrapy_vk_spider")

    def start_requests(self):
        yield Request(self.vk_login_page_url, callback=self.login_then_start_parsing)

    def login_then_start_parsing(self, vk_login_page_response):
        def verify_login_successfully_then_start_parsing(log_in_response, **kwargs):
            self.check_login_response(log_in_response)
            return self.make_start_request()

        form_request = FormRequest.from_response(vk_login_page_response,
                                                 formid="login_form",
                                                 formdata={"email": "79600988916",
                                                           "pass": 'bQ30BIcK'},
                                                 callback=verify_login_successfully_then_start_parsing,
                                                 )
        return form_request

    def make_start_request(self):
        yield Request(url=self.start_url, callback=self.parse)

    def check_login_response(self, response):
        # if redirected to feed then signed in successfully
        if not response.url == "https://m.vk.com/feed":
            raise RuntimeError("authorization failed")

    def parse(self, response, **kwargs):
        for request in self._parse_user(response, **kwargs):
            yield request

    def _parse_user(self, response: Response, **kwargs):
        are_friends_open = self._check_friends_open(response)
        if are_friends_open:
            try:
                friends_href = response.xpath("//div[@class='OwnerInfo__rowCenter']/a").re(
                                              r"friends\?id=\d+")[0]
            except IndexError as e:
                print("error url", response.url)
                print("full page response", response.text)
                raise e
            url_to_friends_page = "https://vk.com/" + friends_href
            print("url to friends page", url_to_friends_page)
            user_friends_request = Request(url_to_friends_page, callback=self._parse_user_friends_list)
            yield user_friends_request

        self._stop_if_needed()  # TODO: move to another part

    def _check_friends_open(self, response: Response) -> bool:
        links_to_friends = response.xpath("//div[@class='OwnerInfo__rowCenter']/a").re(
                                              r"friends\?id=\d+")
        print("Are friends open?", len(links_to_friends) > 0)
        return len(links_to_friends) > 0

    def _parse_user_friends_list(self, response: Response):
        # print("Full friends page text", response.text)
        show_more_friends_href = response.xpath("//a[@class='_show_more Btn Btn_stretch Btn_theme_secondary']/@href").get()
        print("show more", show_more_friends_href)
        if show_more_friends_href:
            print("yielding show more")
            show_more_friends_url = "https://vk.com" + show_more_friends_href
            yield Request(show_more_friends_url, callback=self._parse_user_friends_list, dont_filter=True, method="POST",
                          )

        # TODO: limit number of added and requested friends
        friends_rel_links = response.xpath("//a[@class='OwnerAvatar__link']/@href").getall()
        friends_urls = []
        for link in friends_rel_links:
            if link not in self.storage:  # already visited
                friend_url = "https://vk.com" + link
                friends_urls.append(friend_url)

            # if len(friends_urls) >= self.nb_processed_friends:
            #     break
        print("friends urls", len(friends_urls), friends_urls)
        self.storage.extend(friends_urls)
        # TODO: uncomment
        # for url in friends_urls:
        #     # friend_url = response.url + link
        #     print("friend url", url)
        #     yield Request(url, callback=self._parse_user)

    def _stop_if_needed(self):
        if len(self.storage) >= self.users_needed:
            raise CloseSpider("Enough is enough")
