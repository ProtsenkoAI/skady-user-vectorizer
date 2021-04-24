import vk_api
import requests
from typing import List, Tuple

from interfaces import Credentials


class SessionManager:
    # TODO: add statistics about requests made from every access_token/ ip, number, speed and time of requests
    def __init__(self, proxies: List[Tuple[str, str]], credentials: List[Credentials]):
        self.proxies = proxies
        self.credentials = credentials
        self.session = self._next_session()

    def get_session(self) -> vk_api.VkRequestsPool:
        return self.session

    def reset_session(self):
        self.session = self._next_session()

    def _next_session(self) -> vk_api.VkRequestsPool:
        email, password = self.credentials.pop(0)
        proxy_protocol, proxy_address = self.proxies.pop(0)

        s = requests.Session()
        s.proxies.update({proxy_protocol: proxy_address})

        vk_session = vk_api.VkApi(email, password, session=s)
        return vk_api.requests_pool.VkRequestsPool(vk_session)
