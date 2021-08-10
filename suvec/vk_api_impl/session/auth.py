import requests
import vk_api
import vk_api.exceptions as vk_excepts
from typing import Optional
from .types import SessionData


class BadPasswordError(Exception):
    ...


class CaptchaError(Exception):
    ...


def auth_vk_api(session_data: SessionData,
                user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'
                ) -> Optional[vk_api.VkApi]:
    proxy = session_data.proxy.proxy
    creds = session_data.creds.creds
    s = requests.Session()
    s.headers.update({'User-agent': user_agent})
    for proxy_protocol in ["http", "https"]:
        s.proxies.update({proxy_protocol: proxy.address})
    vk_session = vk_api.VkApi(creds.email, creds.password, session=s)
    try:
        vk_session.auth()
        return vk_session
    except vk_excepts.BadPassword:
        raise BadPasswordError
    except vk_excepts.Captcha:
        raise CaptchaError
