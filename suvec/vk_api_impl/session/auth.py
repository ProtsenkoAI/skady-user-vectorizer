import requests
import vk_api
from typing import Optional
from .types import SessionData
from suvec.common.external_errors_handling import ExternalErrorsHandler


def auth_vk_api(session_data: SessionData,
                errors_handler: ExternalErrorsHandler,
                user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'
                ) -> Optional[vk_api.VkApi]:
    s = requests.Session()
    s.headers.update({'User-agent': user_agent})
    for proxy_protocol in ["http", "https"]:
        s.proxies.update({proxy_protocol: session_data.proxy.address})
    vk_session = vk_api.VkApi(session_data.creds.email, session_data.creds.password, session=s)
    try:
        vk_session.auth()
        return vk_session
    except Exception as e:
        print("error during auth", e)
        auth_data = {"session_data": session_data,
                     "session": vk_session}
        errors_handler.auth_error(e, auth_data=auth_data)
        return None
