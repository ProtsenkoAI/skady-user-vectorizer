import vk_api
from vk_api import requests_pool
import requests

from common.listen_notify import BadPasswordListener
from .records_managing import ProxyManager
from .records_managing import CredsManager
from common.listen_notify import SessionLimitListener


class SessionManager(BadPasswordListener, SessionLimitListener):
    # TODO: add listener.py that enough requests made with this session and need to create new one
    # TODO: maybe move whole session/ component to different product (Skady-Master-Key)
    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'):
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        self.user_agent = user_agent
        self.session = None

    def get_session(self) -> vk_api.VkRequestsPool:
        if self.session is None:
            self.session = self._get_creds_and_proxies_and_reset_session()
        return self.session

    def reset_session_access_error(self):
        self.creds_manager.reset_requests_limit()
        self.proxy_manager.reset_requests_limit()
        self.session = self._get_creds_and_proxies_and_reset_session()

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
                         "proxy protocols": proxy_protocols, "proxy address": proxy_address,
                         "session": vk_session}
            self.errors_handler.auth_error(e, auth_data=auth_data)

        return requests_pool.VkRequestsPool(vk_session)

    def bad_password(self):
        self.creds_manager.reset_bad_password()
        self.session = self._get_creds_and_proxies_and_reset_session()

    def session_limit(self):
        self.creds_manager.reset_requests_limit()
        self.proxy_manager.reset_requests_limit()
        self.session = self._get_creds_and_proxies_and_reset_session()

    def _get_creds_and_proxies_and_reset_session(self):
        email, password = self.creds_manager.get()
        proxy_address, proxy_protocols = self.proxy_manager.get()

        return self._create_session(email, password, proxy_address, proxy_protocols)
