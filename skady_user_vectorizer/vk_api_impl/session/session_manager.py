import vk_api
import requests

from ..bad_password import BadPasswordListener
from .proxy_manager import ProxyManager
from .creds_manager import CredsManager


class SessionManager(BadPasswordListener):
    # TODO: add listener that enough requests made with this session and need to create new one
    # TODO: add statistics about requests made from every access_token/ ip, number, speed and time of requests
    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager):
        self.session = self._next_session()
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager

    def get_session(self) -> vk_api.VkRequestsPool:
        return self.session

    def reset_session(self):
        self.session = self._next_session()

    def _next_session(self) -> vk_api.VkRequestsPool:
        self.proxy_manager.reset()
        self.creds_manager.reset()
        email, password = self.creds_manager.get()
        proxy_address, proxy_protocols = self.proxy_manager.get()

        return self._create_session(email, password, proxy_address, proxy_protocols)

    def _create_session(self, email, password, proxy_address, proxy_protocols):
        s = requests.Session()
        for proxy_protocol in proxy_protocols:
            s.proxies.update({proxy_protocol: proxy_address})
        vk_session = vk_api.VkApi(email, password, session=s)
        try:
            vk_session.auth()
            return vk_api.requests_pool.VkRequestsPool(vk_session)
        except Exception as e:
            auth_data = {"email": email, "password": password,
                         "proxy protocols": proxy_protocols, "proxy address": proxy_address}
            self.errors_handler.auth_error(e, auth_data=auth_data, session=vk_session)

    def bad_password(self):
        self.proxy_manager.reset()
        self.creds_manager.reset()
        email, password = self.creds_manager.get()
        proxy_address, proxy_protocols = self.proxy_manager.get()

        self.session = self._create_session(email, password, proxy_address, proxy_protocols)
