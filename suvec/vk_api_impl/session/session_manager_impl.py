from .records_managing import ProxyManager, CredsManager
from .session_manager import SessionManager
from .types import SessionData


class SessionManagerImpl(SessionManager):
    # TODO: sleep till next day if out of proxy / creds

    # TODO: control number of authorizations on credentials and proxies. Captcha error occurs if ~ > 20 for creds from
    #   different proxies is made or ~ 50 authorizations from proxies are made
    # TODO: note that repeated authorizations of pair are not blocked by captcha

    def __init__(self, proxy_manager: ProxyManager, creds_manager: CredsManager):
        self._last_session_id = -1
        self.proxy_manager = proxy_manager
        self.creds_manager = creds_manager

    def next(self):
        proxy = next(iter(self.proxy_manager.get_working()))
        creds = next(iter(self.creds_manager.get_working()))
        session = SessionData(creds, proxy)
        return session

    def access_error(self, session_data: SessionData):
        # TODO: layer can try to not bad proxy manager, because experiments show that one proxy can handle
        #   many credentials
        self.proxy_manager.mark_worked_out(session_data.proxy)
        self.creds_manager.mark_worked_out(session_data.creds)

    def bad_password(self, session_data: SessionData):
        creds, proxy = session_data.creds, session_data.proxy
        self.creds_manager.mark_bad_password(creds)
        self.proxy_manager.mark_free(proxy)

    def captcha(self, session_data: SessionData):
        # TODO: process captcha errors properly
        self.proxy_manager.mark_worked_out(session_data.proxy)
        self.creds_manager.mark_worked_out(session_data.creds)
