from vk_api import exceptions

from .auth import auth_vk_api
from .sessions_containers import SessionsContainer
from .types import SessionData


class ResourceTester:
    """Makes test request to check if creds and proxy pair works"""

    # TODO: at the moment do not process situation when test resources got AccessError, but it can be.
    #   need to test them too before testing current creds and proxy

    def __init__(self, errors_handler):
        self.sessions_container = SessionsContainer()
        self.errors_handler = errors_handler

    def get_container(self):
        return self.sessions_container

    def test_creds(self, cred):
        working_cred, working_proxy = self._get_session_data()
        return self._test_resources(cred, working_proxy)

    def test_proxy(self, proxy):
        working_cred, working_proxy = self._get_session_data()
        return self._test_resources(working_cred, proxy)

    def _get_session_data(self):
        _, session_data = self.sessions_container.get()[0]
        creds, proxy = session_data
        return creds, proxy

    def _test_resources(self, creds, proxy):
        session = auth_vk_api(SessionData(creds=creds, proxy=proxy), self.errors_handler, session_id=-999)
        if session is None:
            return False
        try:
            res = session.method("groups.get", values={"user_ids": 1})
            return True
        except exceptions.ApiError:
            print("Test failed")
            return False
