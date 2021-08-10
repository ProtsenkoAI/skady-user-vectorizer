from .records_managing import ProxyManager, CredsManager
from .session_manager import SessionManager
from .types import SessionData


class OutOfRecords(Exception):
    ...


class SessionManagerImpl(SessionManager):
    # IMPROVE: control number of authorizations on credentials and proxies. Captcha error occurs if ~ > 20 for creds
    #   from different proxies is made or ~ 50 authorizations from proxies are made(note that repeated
    #   authorizations of pair are not blocked by captcha)

    def __init__(self, proxy_manager: ProxyManager, creds_manager: CredsManager):
        self._last_session_id = -1
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager

    def next(self):
        try:
            proxy = next(iter(self.proxy_manager.get_working()))
            creds = next(iter(self.creds_manager.get_working()))
        except StopIteration:
            raise OutOfRecords
        session = SessionData(creds, proxy)
        return session

    def access_error(self, session_data: SessionData):
        # IMPROVE: experiments show that one proxy can handle many credentials, so can use it to optimize resources
        self.proxy_manager.mark_worked_out(session_data.proxy)
        self.creds_manager.mark_worked_out(session_data.creds)

    def bad_password(self, session_data: SessionData):
        creds, proxy = session_data.creds, session_data.proxy
        self.creds_manager.mark_bad_password(creds)
        self.proxy_manager.mark_free(proxy)

    def captcha(self, session_data: SessionData):
        # IMPROVE: process captcha errors properly
        self.proxy_manager.mark_worked_out(session_data.proxy)
        self.creds_manager.mark_worked_out(session_data.creds)
