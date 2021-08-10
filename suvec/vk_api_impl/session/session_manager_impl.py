from typing import List

from suvec.common.listen_notify import SessionErrorListener
from .records_managing import ProxyManager, CredsManager
from .session_manager import SessionManager
from .records_managing.records import CredsRecord, ProxyRecord
from .types import SessionData
from .sessions_containers import SessionsContainer, BadSession
from .records_managing.consts import RESOURCE_ALREADY_USED


class SessionManagerImpl(SessionManager, SessionErrorListener):
    # TODO: (checked logs) sometimes we mark session as bad because of Captcha needed, then test creds and proxy,
    #   and both of them succeed. Thus, we maybe should mark THE PAIR as bad, but not resources separately

    # TODO: control number of authorizations on credentials and proxies. Captcha error occurs if ~ > 20 for creds from
    #   different proxies is made or ~ 50 authorizations from proxies are made

    # TODO: note that repeated authorizations of pair are not blocked by captcha

    # TODO: separate access error managing for friends and groups requests
    def __init__(self, errors_handler, proxy_manager: ProxyManager, creds_manager: CredsManager):
        self._last_session_id = -1
        self.errors_handler = errors_handler
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager
        self.sessions_containers: List[SessionsContainer] = []

    def allocate_sessions(self, n: int, container: SessionsContainer):
        # TODO: it's inconvenient to create container every time, but we need to support different container subclass,
        #   maybe we can find better solution
        session_idx = 0
        for proxy, creds in zip(self.proxy_manager.get_working(),
                                self.creds_manager.get_working()):
            self._last_session_id += 1
            session = self._create_session(proxy, creds)
            try:
                container.add(session, self._last_session_id)
                if session_idx == n - 1:
                    break
                session_idx += 1

            except BadSession:
                self._handle_bad_session(creds, proxy)

        self.sessions_containers.append(container)

    def _create_session(self, proxy: ProxyRecord, creds: CredsRecord):
        return SessionData(creds, proxy)

    def session_error_occurred(self, session_id: int):
        session_data = self._get_session_data_by_id(session_id)
        if session_data is not None:  # will be None if already deleted this session
            self.mark_worked_out(session_data)
            self._replace_session(session_id)

    def mark_worked_out(self, session_data):
        creds, proxy = session_data.creds, session_data.proxy
        self.creds_manager.mark_worked_out(creds)
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
        # TODO: refactor try/except
        for container in self.sessions_containers:
            if container.check_in(session_id):
                container.remove(session_id)
                working_creds = self.creds_manager.get_working()
                working_proxies = self.proxy_manager.get_working()
                while True:
                    try:
                        creds, proxies = next(working_creds), next(working_proxies)
                        try:
                            container.add(self._create_session(creds=creds, proxy=proxies), self._last_session_id)
                            self._last_session_id += 1
                            break
                        except BadSession:
                            self._handle_bad_session(creds, proxies)

                    except StopIteration:
                        print("have no creds/proxies, don't add new session")
                        raise RuntimeError("Out of session resources")
                break

        else:
            raise RuntimeError(f"Session id {session_id} was not found in containers")

    def get_new_session(self):
        # TODO: dirty function for replace() realization in containers, will refactor later
        working_creds = self.creds_manager.get_working()
        working_proxies = self.proxy_manager.get_working()
        try:
            creds, proxies = next(working_creds), next(working_proxies)
            try:
                session = self._create_session(creds=creds, proxy=proxies)
                self._last_session_id += 1
                return session, self._last_session_id
            except BadSession:
                self._handle_bad_session(creds, proxies)
        except StopIteration:
            return None, None

    def _handle_bad_session(self, creds, proxies):
        # TODO: write tests, buggy place
        print("handling bad session", "creds status", creds.status, "proxy status", proxies.status)
        assert creds.status == RESOURCE_ALREADY_USED
        assert proxies.status == RESOURCE_ALREADY_USED
        # if creds.status == RESOURCE_ALREADY_USED:
        self.creds_manager.mark_worked_out(creds)
        self.proxy_manager.mark_worked_out(proxies)
        # if proxies.status == RESOURCE_ALREADY_USED:
        #     self.proxy_manager.mark_free(proxies)

    def get_errors_handler(self):
        return self.errors_handler
