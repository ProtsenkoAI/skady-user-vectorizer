from vk_api import exceptions

from .auth import auth_vk_api


class ResourceTester:
    """Makes test request to check if creds and proxy pair works"""

    # TODO: at the moment do not process situation when test resources got AccessError, but it can be.
    #   need to test them too before testing current creds and proxy

    def __init__(self, sessions_container):
        # TODO: refactor this infinity-loop connection
        self.sessions_container = sessions_container

    def test_cred(self, cred_with_id):
        working_cred, working_proxy = self._get_session_data()
        return self._test_resources(cred_with_id, working_proxy)

    def test_proxy(self, proxy_with_id):
        working_cred, working_proxy = self._get_session_data()
        return self._test_resources(working_cred, proxy_with_id)

    def _get_session_data(self):
        _, session_data = self.sessions_container.get()[0]
        creds, proxy = session_data
        return creds, proxy

    def _test_resources(self, creds, proxy):
        session, session_id = auth_vk_api(creds, proxy)
        if session is None:
            return False
        try:
            res = session.vk_session.method("groups.get", values={"user_ids": 1})
            return True
        except exceptions.ApiError:
            print("Test failed")
            return False
