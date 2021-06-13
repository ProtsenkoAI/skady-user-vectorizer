from typing import List, Tuple, Optional, Dict
import vk_api
from vk_api import exceptions
from vk_api import requests_pool
import requests

from suvec.common.listen_notify import BadPasswordListener, AccessErrorListener
from .records_managing import ProxyManager, CredsManager
from suvec.common.executing import ParseRes

CredProxyIds = Tuple[int, int]
Creds = Tuple[str, str]
Proxy = str


class SessionManager(BadPasswordListener, AccessErrorListener):
    # TODO: now we have aiovk realisation, and it doesn't need vk_api.VkRequestsPool, so maybe create data structure
    #   *session* and only then convert it to vk_api or aiovk variants?
    # TODO: unittests
    # NOTE: reserving one pair of cred and proxy for test requests, maybe its not effective
    SessionWithId = Tuple[vk_api.VkRequestsPool, int]

    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'):
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        self.user_agent = user_agent

        self.session_id_to_session_info: Dict[int, Tuple[CredProxyIds,
                                                         Tuple[Proxy, Creds],
                                                         requests_pool.VkRequestsPool]] = {}
        self.met_creds_ids = set()
        self.met_proxy_ids = set()

        self.test_cred: Tuple[Creds, int] = self._get_new_and_add_to_met(self.creds_manager.resources(),
                                                                         self.met_creds_ids)
        self.test_proxy: Tuple[Proxy, int] = self._get_new_and_add_to_met(self.proxy_manager.resources(),
                                                                          self.met_proxy_ids)
        self.resource_tester = ResourceTester(self.test_cred, self.test_proxy, self)

        self.last_session_id = -1

    def get_n_sessions(self, n) -> List[SessionWithId]:
        print("called get_n_sessions, nb of sessions available", len(self.session_id_to_session_info))
        while len(self.session_id_to_session_info) < n:
            self._make_new_session()

        sessions = [(session, session_id) for session_id, (ids, resources, session) in
                    list(self.session_id_to_session_info.items())[:n]]
        print("returning n sessions:", self.session_id_to_session_info)
        return sessions

    def get_next_session(self) -> SessionWithId:
        if not self.session_id_to_session_info:
            self._make_new_session()
        session_id = next(iter(self.session_id_to_session_info.keys()))
        _, _, session = self.session_id_to_session_info[session_id]

        return session, session_id

    def _make_new_session(self):
        print("called _make_new_session")
        cred, cred_id = self._get_new_and_add_to_met(
            self.creds_manager.resources(self.resource_tester.test_cred), self.met_creds_ids
        )
        proxy, proxy_id = self._get_new_and_add_to_met(
            self.proxy_manager.resources(self.resource_tester.test_proxy), self.met_proxy_ids
        )
        session, session_id = self.create_new_session((cred, cred_id), (proxy, proxy_id))
        self.session_id_to_session_info[session_id] = ((cred_id, proxy_id),
                                                       (proxy, cred),
                                                       session)

    def create_new_session(self, cred: Tuple[Creds, int], proxy: Tuple[Proxy, int]):
        print("called create_save_session with cred", cred, "and proxy", proxy)
        (email, password), creds_id = cred
        proxy_address, proxy_id = proxy
        self.last_session_id += 1
        session, _ = self._create_session(email, password, proxy_address, self.last_session_id), self.last_session_id

        return session, self.last_session_id

    def access_error_occurred(self, parse_res: ParseRes):
        print("access error occured")
        session_id = parse_res.session_id
        (creds_id, proxy_id), (proxy, creds), _ = self.session_id_to_session_info[session_id]
        del self.session_id_to_session_info[session_id]

        creds_test_succ = self.resource_tester.test_cred((creds, creds_id))
        proxy_test_res = self.resource_tester.test_proxy((proxy, proxy_id))

        if not creds_test_succ:
            self.creds_manager.reset_requests_limit(creds_id)
        if not proxy_test_res:
            self.proxy_manager.reset_requests_limit(proxy_id)

    def bad_password(self, session_id):
        if session_id in self.session_id_to_session_info:
            (creds_id, _), _, _ = self.session_id_to_session_info[session_id]
            del self.session_id_to_session_info[session_id]
            self.creds_manager.mark_bad_password(creds_id)
        else:
            # bad password with already deleted/ not added session, skip
            pass

    def _create_session(self, email, password, proxy_address, session_id) -> Optional[requests_pool.VkRequestsPool]:
        s = requests.Session()
        s.headers.update({'User-agent': self.user_agent})
        for proxy_protocol in ["http", "https"]:
            s.proxies.update({proxy_protocol: proxy_address})
        vk_session = vk_api.VkApi(email, password, session=s)
        try:
            vk_session.auth()
        except Exception as e:
            print("error during auth", e)
            auth_data = {"email": email, "password": password,
                         "proxy address": proxy_address,
                         "session": vk_session}
            self.errors_handler.auth_error(e, auth_data=auth_data, session_id=session_id)
            return None
        return requests_pool.VkRequestsPool(vk_session)

    @staticmethod
    def _get_new_and_add_to_met(records, met_ids: set):
        for record, rec_id in records:
            if rec_id not in met_ids:
                met_ids.add(rec_id)
                return record, rec_id


class ResourceTester:
    """Makes test request to check if creds and proxy pair works"""

    # TODO: at the moment do not process situation when test resources got AccessError, but it can be.
    #   need to test them too before testing current creds and proxy

    def __init__(self, cred, proxy, session_manager):
        self.cred = cred
        self.proxy = proxy
        # TODO: refactor this infinity-loop connection
        self.session_manager = session_manager

    def test_cred(self, cred_with_id):
        return self._test_resources(cred_with_id, self.proxy)

    def test_proxy(self, proxy_with_id):
        return self._test_resources(self.cred, proxy_with_id)

    def _test_resources(self, cred_with_id, proxy_with_id):
        print("Testing resources", cred_with_id, proxy_with_id)
        session, session_id = self.session_manager.create_new_session(cred_with_id, proxy_with_id)
        if session is None:
            return False
        # TODO: need separate component to do it
        try:
            res = session.vk_session.method("groups.get", values={"user_ids": 1})
            return True
        except exceptions.ApiError:
            print("Test failed")
            return False
