from typing import List

from suvec.common.listen_notify import SessionErrorListener
from suvec.common.executing import ParseRes
from .records_managing import ProxyManager, CredsManager
from .session_manager import SessionManager
from .records_managing.records import CredsRecord, ProxyRecord
from .resource_testing import ResourceTester
from .types import SessionData
from .sessions_containers import SessionsContainer, BadSession


class SessionManagerImpl(SessionManager, SessionErrorListener):
    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager,
                 tester: ResourceTester):
        self._last_session_id = -1
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        self.sessions_containers: List[SessionsContainer] = []
        self.allocate_sessions(1, tester.get_container())
        self.resource_tester = tester

    def allocate_sessions(self, n: int, container: SessionsContainer):
        # TODO: it's inconvenient to create container every time, but we need to support different container subclass,
        #   maybe we can find better solution
        session_idx = 0
        for proxy, creds in zip(self.proxy_manager.get_working(), self.creds_manager.get_working()):
            self._last_session_id += 1
            try:
                container.add(self._create_session(proxy, creds), self._last_session_id)
                if session_idx == n - 1:
                    break
                session_idx += 1
            except BadSession:
                self._test_and_reset_resources_statuses(creds, proxy)

        self.sessions_containers.append(container)

    def _create_session(self, proxy: ProxyRecord, creds: CredsRecord):
        return SessionData(creds, proxy)

    def session_error_occurred(self, session_id: int):
        session_data = self._get_session_data_by_id(session_id)
        if session_data is not None:  # will be None if already deleted this session
            creds, proxy = session_data.creds, session_data.proxy
            self._test_and_reset_resources_statuses(creds, proxy)
            self._replace_session(session_id)

    def _test_and_reset_resources_statuses(self, creds, proxy):
        creds_test_succ = self.creds_manager.test_with_record_tester(self.resource_tester, creds)
        proxy_test_succ = self.proxy_manager.test_with_record_tester(self.resource_tester, proxy)
        if creds_test_succ:
            self.creds_manager.mark_free(creds)
        else:
            self.creds_manager.mark_worked_out(creds)
        if proxy_test_succ:
            self.proxy_manager.mark_free(proxy)
        else:
            self.proxy_manager.mark_worked_out(proxy)

    def bad_password(self, session_id):
        session_data = self._get_session_data_by_id(session_id)
        if session_data is not None:
            creds, proxy = session_data.creds, session_data.proxy
            self.creds_manager.mark_bad_password(creds)
            self.proxy_manager.mark_free(proxy)
            self._replace_session(session_id)

    def proxy_error_occurred(self, session_id: int):
        session_data = self._get_session_data_by_id(session_id)
        if session_data is not None:
            creds, proxy = session_data.creds, session_data.proxy
            self.creds_manager.mark_free(creds)
            self.proxy_manager.mark_worked_out(proxy)
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
                    self._last_session_id += 1
                    container.add(self._create_session(creds=creds, proxy=proxies), self._last_session_id)
                except StopIteration:
                    print("have no creds/proxies, don't add new session")
                finally:
                    break

    def get_errors_handler(self):
        return self.errors_handler
