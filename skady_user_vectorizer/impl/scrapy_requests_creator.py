from typing import Callable
from scrapy import Request, FormRequest
from scrapy.http import Response

from ..interfaces import RequestsCreator, User, Credentials


class ScrapyRequestsCreator(RequestsCreator):
    # TODO: pass creds in more safe way
    # TODO: test
    def __init__(self, func_to_get_requests: Callable, creds: Credentials):
        self.get_requests = func_to_get_requests
        self.vk_login_page_url = "https://login.vk.com/?act=login"
        self.creds = creds

    def auth_request(self, callback: Callable) -> Request:
        # First get login page, then submit form data to login, then call the callback for login submit form response
        yield Request(self.vk_login_page_url, callback=self._wrap_login_then_call_callback(callback))

    def _wrap_login_then_call_callback(self, callback: Callable):
        def wrapped(login_page_response: Response):
            form_request = FormRequest.from_response(login_page_response,
                                                     formid="login_form",
                                                     formdata={"email": self.creds.email,
                                                               "password": self.creds.password},
                                                     callback=callback,
                                                     )
            return form_request

        return wrapped

    def change_proxy(self):
        raise NotImplementedError("Proxies are not currently supported :<")

    def friends_request(self, candidate: User, callback: Callable) -> Request:
        request = Request(url="https://vk.com/al_friends.php",
                          method="POST",
                          headers={"act": "load_friends_silent",
                                   "oid": candidate.id,
                                   "tab": "friends"},
                          callback=callback
                          )
        return request

    def groups_request(self, candidate: User, callback: Callable) -> Request:
        request = Request(url="https://vk.com/al_fans.php",
                          method="POST",
                          headers={"act": "load_idols",
                                   "oid": candidate.id},
                          callback=callback
                          )
        return request

    def wrap_callback(self, callback: Callable) -> Callable:
        """To schedule new requests in scrapy you need to return them from callback
        thus the wrapped callback will receive new requests and return it"""
        def wrapped_callback(*args, **kwargs):
            callback(*args, **kwargs)
            return self.get_requests()
        return wrapped_callback
