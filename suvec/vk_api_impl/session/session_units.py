from .auth import auth_vk_api, BadPasswordError, CaptchaError

import vk_api
import aiovk
from aiovk import drivers

from typing import Tuple, NamedTuple


class TokenSessionWithProxyMaker:
    """wrapper for AsyncVkExecuteRequestPool from aiovk because it doesn't support passing
    Driver to session"""

    def __init__(self, proxy_ip, proxy_port):
        self.proxy_ip, self.proxy_port = proxy_ip, proxy_port

    def __call__(self, token):
        proxy_driver = drivers.ProxyDriver(self.proxy_ip, self.proxy_port)
        return aiovk.TokenSession(token, driver=proxy_driver)


AioSession = NamedTuple("AioSession", [("session", TokenSessionWithProxyMaker),
                                       ("access_token", str)]
                        )


class SessionUnit:
    def __init__(self, session_manager):
        self.session_obj = None
        self.session_data = None

        self.session_manager = session_manager
        self.refresh_data()

    def refresh_data(self):
        self.session_obj = self.session_manager.next()
        self.session_data = self.session_obj

    def get(self):
        return self.session_obj

    def access_error_occurred(self):
        """Tells Sessions Manager about access error and refreshes own resources"""
        self.session_manager.access_error(self.session_data)
        self.refresh_data()


class AioVkSessionUnit(SessionUnit):
    def refresh_data(self):
        super().refresh_data()
        try:
            vk_session = auth_vk_api(self.session_obj)
        except BadPasswordError:
            self.session_manager.bad_password(self.session_data)
            self.refresh_data()
        except CaptchaError:
            self.session_manager.captcha(self.session_data)
            self.refresh_data()
        except ConnectionResetError:
            print("ConnectionResetError!")
            # Caution: can enter infinite loop if server always will give this error
            self.refresh_data()
        else:
            proxy_ip, proxy_port = self._extract_proxy(vk_session)
            token_session = TokenSessionWithProxyMaker(proxy_ip, proxy_port)
            access_token = vk_session.token["access_token"]
            self.session_obj = AioSession(token_session, access_token)

    def _extract_proxy(self, vk_api_session: vk_api.VkApi) -> Tuple[str, str]:
        requests_session = vk_api_session.http
        proxy = requests_session.proxies["http"]
        return proxy.split(":")
