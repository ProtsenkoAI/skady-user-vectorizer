import vk_api
from vk_api import requests_pool
import requests

from ..bad_password import BadPasswordListener
from ..session.proxy_manager import ProxyManager
from ..session.creds_manager import CredsManager


class SessionManager(BadPasswordListener):
    # TODO: add listener that enough requests made with this session and need to create new one
    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'):
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        self.user_agent = user_agent
        self.session = None

    def get_session(self) -> vk_api.VkRequestsPool:
        if self.session is None:
            self.session = self._next_session()
        return self.session

    def reset_session(self):
        self.session = self._next_session()

    def _next_session(self) -> vk_api.VkRequestsPool:
        self.proxy_manager.reset()
        self.creds_manager.reset()
        email, password = self.creds_manager.get()
        proxy_address, proxy_protocols = self.proxy_manager.get()

        return self._create_session(email, password, proxy_address, proxy_protocols)

    def _create_session(self, email, password, proxy_address, proxy_protocols) -> requests_pool.VkRequestsPool:
        s = requests.Session()
        s.headers.update({'User-agent': self.user_agent})
        for proxy_protocol in proxy_protocols:
            s.proxies.update({proxy_protocol: proxy_address})
        vk_session = vk_api.VkApi(email, password, session=s)
        try:
            vk_session.auth()
        except Exception as e:
            auth_data = {"email": email, "password": password,
                         "proxy protocols": proxy_protocols, "proxy address": proxy_address}
            self.errors_handler.auth_error(e, auth_data=auth_data, session=vk_session)

        return requests_pool.VkRequestsPool(vk_session)

    def bad_password(self):
        self.creds_manager.reset()
        email, password = self.creds_manager.get()
        proxy_address, proxy_protocols = self.proxy_manager.get()

        self.session = self._create_session(email, password, proxy_address, proxy_protocols)
