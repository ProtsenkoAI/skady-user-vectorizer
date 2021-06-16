from typing import List

from suvec.common.listen_notify import BadPasswordListener, AccessErrorListener
from .records_managing import ProxyManager, CredsManager
from .session_manager import SessionManager
from .records_managing.records import Proxy, Credentials
from .resource_testing import ResourceTester
from .types import SessionData
from .sessions_containers import SessionsContainer


class SessionManagerImpl(SessionManager, BadPasswordListener, AccessErrorListener):
    # TODO: unittests

    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager):
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        tester_container = SessionsContainer()
        self.sessions_containers: List[SessionsContainer] = []
        self.allocate_sessions(1, tester_container)
        self.resource_tester = ResourceTester(tester_container, self.errors_handler)

    def allocate_sessions(self, n: int, container: SessionsContainer):
        for proxy, cred, _ in zip(self.proxy_manager.get_working(), self.creds_manager.get_working(), range(n)):
            container.add(self._create_session(proxy, cred))
        self.sessions_containers.append(container)

    def _create_session(self, proxy: Proxy, creds: Credentials):
        return SessionData(creds, proxy)

    def access_error_occurred(self, parse_res):
        session_data = self._get_session_data_by_id(parse_res.session_id)
        if session_data is not None:  # will be None if already deleted this session
            creds, proxy = session_data.creds, session_data.proxy

            creds_test_succ = self.resource_tester.test_cred(creds)
            proxy_test_succ = self.resource_tester.test_proxy(proxy)

            if creds_test_succ:
                self.creds_manager.mark_free(creds)
            else:
                self.creds_manager.mark_worked_out(creds)
            if proxy_test_succ:
                self.proxy_manager.mark_free(proxy)
            else:
                self.proxy_manager.mark_worked_out(proxy)
            self._replace_session(parse_res.session_id)

    def bad_password(self, session_id):
        session_data = self._get_session_data_by_id(session_id)
        if session_data is not None:
            creds, proxy = session_data.creds, session_data.proxy
            self.creds_manager.mark_bad_password(creds)
            self.proxy_manager.mark_free(proxy)
            self._replace_session(session_id)

    def _get_session_data_by_id(self, session_id: int):
        for container in self.sessions_containers:
            if container.check_in(session_id):
                return container.get_data(session_id)

    def _replace_session(self, session_id: int):
        for container in self.sessions_containers:
            if container.check_in(session_id):
                container.remove(session_id)
                try:
                    creds, proxies = next(self.creds_manager.get_working()), next(self.proxy_manager.get_working())
                    container.add(self._create_session(creds=creds, proxy=proxies))
                    break
                except StopIteration:
                    print("have no creds/proxies, don't add new session")

    def get_errors_handler(self):
        return self.errors_handler
