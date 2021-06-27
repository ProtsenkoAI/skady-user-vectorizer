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

    def check_in(self, session_id: int):
        return session_id in self.sessions_data

    def remove(self, session_id: int):
        del self.sessions_data[session_id]

    def add(self, session_data: SessionData, session_id):
        self.sessions_data[session_id] = session_data

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


class BadSession(ValueError):
    """Can't use provided session for some reason"""


class AioVkSessionsContainer(SessionsContainer):
    # TODO: sometimes not-working sessions are added to container, need tests for this situations

    # TODO: add test, that if bad session was added, then both self.aiovk_sessions dict and self.sessions_data aren't
    #   updated
    def __init__(self, *args, errors_handler, **kwargs):
        super().__init__()
        self.errors_handler = errors_handler
        self.aiovk_sessions: Dict[int, AioSession] = {}

    def add(self, session_data: SessionData, session_id):
        self.aiovk_sessions[session_id] = self._create_aio_session(session_data, session_id)
        super().add(session_data, session_id)

    def get(self) -> List[Tuple[int, AioSession]]:
        if len(self.aiovk_sessions.items()) == 0:
            # TODO: handle it with out of resources components
            raise RuntimeError("Have no working sessions left")

        return list(self.aiovk_sessions.items())

    def remove(self, session_id: int):
        super().remove(session_id)
        del self.aiovk_sessions[session_id]

    def _create_aio_session(self, session_data: SessionData, session_id) -> AioSession:
        vk_session = auth_vk_api(session_data, self.errors_handler, session_id)
        if vk_session is None:
            raise BadSession()
        proxy_ip, proxy_port = self._extract_proxy(vk_session)
        token_session = TokenSessionWithProxyMaker(proxy_ip, proxy_port)
        access_token = vk_session.token["access_token"]
        return AioSession(token_session, access_token, session_data)

    def _extract_proxy(self, vk_api_session: vk_api.VkApi) -> Tuple[str, str]:
        # TODO: process case when auth_vk_api returns None
        requests_session = vk_api_session.http
        proxy = requests_session.proxies["http"]
        return proxy.split(":")


class VkApiSessionsContainer(SessionsContainer):
    def __init__(self, *args, errors_handler, **kwargs):
        super().__init__()
        self.errors_handler = errors_handler
        self.vk_api_sessions: Dict[int, VkRequestsPool] = {}

    def add(self, session_data: SessionData, session_id):
        super().add(session_data, session_id)
        self.vk_api_sessions[session_id] = self._create_vk_api_pool(session_data, session_id)

    def get(self) -> List[Tuple[int, VkRequestsPool]]:
        return list(self.vk_api_sessions.items())

    def remove(self, session_id: int):
        super().remove(session_id)
        del self.vk_api_sessions[session_id]

    def _create_vk_api_pool(self, session_data: SessionData, session_id: int) -> VkRequestsPool:
        vk_session = auth_vk_api(session_data, self.errors_handler, session_id)
        return VkRequestsPool(vk_session)
