from typing import Callable
from scrapy import Request, FormRequest
from scrapy.http import Response

from interfaces import RequestsCreator, User, Credentials


class ScrapyRequestsCreator(RequestsCreator):
    # TODO: move each request realisation to separate class, thus this component will be abstract fabric
    # NOTE: we want to use proxies, but FindClone / any search engine somehow crawls a LOT of pages
    #   so think /read how they do it.
    # NOTE: at the moment authorization doesn't work properly, but vk_api python wrapper lib has
    #   ready code for that. Check: https://github.com/python273/vk_api/blob/master/vk_api/vk_api.py
    # TODO: pass creds in more safe way
    # TODO: imitate real requests headers using helper object (user-agent, host etc)
    def __init__(self, creds: Credentials):
        self.get_requests = None
        # self.vk_login_page_url = "https://login.vk.com/?act=login&role=al_frame"
        self.start_vk_page_url = "https://vk.com/"
        self.creds = creds

        # self.other_headers = {
            # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            #           "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",

            # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            # "accept-encoding": "gzip, deflate, br",
            # "accept-language": "en-US,en;q=0.9",
            # "dnt": "1",
            # "sec-fetch-dest": "document",
            # "sec-fetch-mode": "navigate",
            # "sec-fetch-site": "none",
            # "sec-fetch-user": "?1",
            # "upgrade-insecure-requests": "1",
            # "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            # "sec-ch-ua-mobile": "?0"
        # }
        # self.other_headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KH'
        #                                     'TML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                              # 'Accept-Encoding': 'gzip, deflate',
                              # 'Accept': '*/*',
                              # 'Connection': 'keep-alive'
                              # }

    def set_get_requests_callable(self, get_requests: Callable):
        # TODO: refactor architecture and eliminate this method
        self.get_requests = get_requests

    def auth_request(self, callback: Callable) -> Request:
        # First get login page, then submit form data to login, then call the callback for login submit form response
        # TODO: wrap in more convenient way
        callback_returning_requests = self._wrap_callback(callback)
        yield Request(self.start_vk_page_url,
                      callback=self._wrap_login_then_call_callback(callback_returning_requests)
                      )

    def _wrap_login_then_call_callback(self, callback: Callable):
        # TODO: refactor (esp names
        def wrapped(login_page_response: Response):
            print("start page response", login_page_response.url)
            print("start page request headers", login_page_response.request.headers)
            print("start page headers", login_page_response.headers)
            # print("start page text", login_page_response.text)
            # Now requesting form with login
            # request = FormRequest.from_response(login_page_response,
            #                                     formid="login_form",
            #                                     formdata={"email": self.creds.email,
            #                                               "pass": self.creds.password},
            #                                     callback=callback,
            #                                     )
            request = Request("https://login.vk.com/?act=login", callback=self._refactor_later_process_login_page)
            return request

        return wrapped

    def _refactor_later_process_login_page(self, response: Response):
        print("login page response", response.url)

    def change_proxy(self):
        raise NotImplementedError("Proxies are not currently supported :<")

    def friends_request(self, candidate: User, callback: Callable) -> Request:
        callback_returning_requests = self._wrap_callback(callback)
        request = Request(url="https://vk.com/al_friends.php",
                          method="POST",
                          headers={"act": "load_friends_silent",
                                   "al": 1,
                                   "id": candidate.id,
                                   **self.other_headers},
                          callback=callback_returning_requests
                          )
        return request

    def groups_request(self, candidate: User, callback: Callable) -> Request:
        callback_returning_requests = self._wrap_callback(callback)
        request = Request(url="https://vk.com/al_fans.php",
                          method="POST",
                          headers={"act": "load_idols",
                                   "oid": candidate.id,
                                   **self.other_headers},
                          callback=callback_returning_requests,
                          )
        return request

    def _wrap_callback(self, callback: Callable) -> Callable:
        if self.get_requests is None:
            raise RuntimeError("called creator method without setting get_requests callable. "
                               "Use set_get_requests_callable for this purpose")
        """To schedule new requests in scrapy you need to return them from callback
        thus the wrapped callback will receive new requests and return it"""

        def wrapped_callback(*args, **kwargs):
            callback(*args, **kwargs)
            return self.get_requests()

        return wrapped_callback
