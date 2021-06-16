from typing import List, NamedTuple, Tuple, Dict

import aiovk
from aiovk import drivers
import vk_api
from vk_api.requests_pool import VkRequestsPool

from .auth import auth_vk_api
from .types import SessionData


class SessionsContainer:
    """Container with session objects. Sessions can be inserted from session manager"""
    def __init__(self):
        self.sessions_data: Dict[int, SessionData] = {}
        self.last_session_id = -1

    def check_in(self, session_id: int):
        return session_id in self.sessions_data

    def remove(self, session_id: int):
        del self.sessions_data[session_id]

    def add(self, session_data: SessionData):
        self.last_session_id += 1
        self.sessions_data[self.last_session_id] = session_data

    def get_data(self, session_id):
        """Internal method for errors processing"""
        return self.sessions_data[session_id]

    def get(self) -> List[Tuple[int, SessionData]]:
        return list(self.sessions_data.items())


class TokenSessionWithProxyMaker:
    """wrapper for AsyncVkExecuteRequestPool from aiovk because it doesn't support passing
    Driver to session"""

    def __init__(self, proxy_ip, proxy_port):
        self.proxy_ip, self.proxy_port = proxy_ip, proxy_port

    def __call__(self, token):
        proxy_driver = drivers.ProxyDriver(self.proxy_ip, self.proxy_port)
        return aiovk.TokenSession(token, driver=proxy_driver)


AioSession = NamedTuple("AioSession", [("session", TokenSessionWithProxyMaker),
                                       ("access_token", str),
                                       ("data", SessionData)])


class AioVkSessionsContainer(SessionsContainer):
    def __init__(self, *args, errors_handler, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors_handler = errors_handler
        self.aiovk_sessions: Dict[int, AioSession] = {}

    def add(self, session_data: SessionData):
        super().add(session_data)
        self.aiovk_sessions[self.last_session_id] = self._create_aio_session(session_data)

    def get(self):
        return list(self.aiovk_sessions.items())

    def remove(self, session_id: int):
        super().remove(session_id)
        del self.aiovk_sessions[session_id]

    def _create_aio_session(self, session_data: SessionData) -> AioSession:
        vk_session = auth_vk_api(session_data, self.errors_handler)
        proxy_ip, proxy_port = self._extract_proxy(vk_session)
        token_session = TokenSessionWithProxyMaker(proxy_ip, proxy_port)
        access_token = vk_session.token["access_token"]
        return AioSession(token_session, access_token, session_data)

    def _extract_proxy(self, vk_api_session: vk_api.VkApi) -> Tuple[str, str]:
        requests_session = vk_api_session.http
        proxy = requests_session.proxies["http"]
        return proxy.split(":")


class VkApiSessionsContainer(SessionsContainer):
    def __init__(self, *args, errors_handler, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors_handler = errors_handler
        self.vk_api_sessions: Dict[int, VkRequestsPool] = {}

    def add(self, session_data: SessionData):
        super().add(session_data)
        self.vk_api_sessions[self.last_session_id] = self._create_vk_api_pool(session_data)

    def get(self) -> List[Tuple[int, VkRequestsPool]]:
        return list(self.vk_api_sessions.items())

    def remove(self, session_id: int):
        super().remove(session_id)
        del self.vk_api_sessions[session_id]

    def _create_vk_api_pool(self, session_data: SessionData) -> VkRequestsPool:
        vk_session = auth_vk_api(session_data, self.errors_handler)
        return VkRequestsPool(vk_session)
