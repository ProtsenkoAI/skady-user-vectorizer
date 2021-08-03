from vk_api import exceptions

from .auth import auth_vk_api
from .sessions_containers import SessionsContainer
from suvec.common.listen_notify import SessionErrorNotifier
from .types import SessionData
from .records_managing.consts import RESOURCE_WORKED_OUT_STATUS


class ResourceTester(SessionErrorNotifier):
    """Makes test request to check if creds and proxy pair works"""
    # TODO: very buggy component, need unittests
    # TODO: Do not have normal interface to replace working session of tester with session_manager, so using crutches
    #   in test_creds() and test_proxies(). Needs refactoring

    def __init__(self, errors_handler, check_own_resources_every=5):
        """
        :param check_own_resources_every: if test fails, increases count for proxy or credential, if n test are failed
            with some tester resource, it's being tested with paired tester resource, and if test is failed, we push
            session_error
        """
        super().__init__()
        self.sessions_container = SessionsContainer()
        self.errors_handler = errors_handler
        self.proxy_failed_checks_cnt = 0
        self.creds_failed_checks_cnt = 0
        self.check_own_resources_every = check_own_resources_every

    def get_container(self):
        return self.sessions_container

    def test_creds(self, cred):
        working_creds, working_proxy = self._get_session_data()
        if cred == working_creds:
            return False  # check todo in header
        test_success = self._test_resources(cred, working_proxy)

        if not test_success:
            self.proxy_failed_checks_cnt += 1
            if self.proxy_failed_checks_cnt == self.check_own_resources_every:
                self._test_own_resources()
                self.proxy_failed_checks_cnt = 0
        return test_success

    def test_proxy(self, proxy):
        working_cred, working_proxy = self._get_session_data()
        if proxy == working_proxy:
            return False  # check todo in header
        test_success = self._test_resources(working_cred, proxy)

        if not test_success:
            self.creds_failed_checks_cnt += 1
            if self.creds_failed_checks_cnt == self.check_own_resources_every:
                self._test_own_resources()
                self.creds_failed_checks_cnt = 0
        return test_success

    def _test_own_resources(self):
        print("testing own resources")
        own_creds, own_proxy = self._get_session_data()
        test_res = self._test_resources(own_creds, own_proxy)
        if not test_res:
            own_session_id, _ = self.sessions_container.get()[0]
            self.notify_session_error(own_session_id)

    def _get_session_data(self):
        _, session_data = self.sessions_container.get()[0]
        creds, proxy = session_data
        return creds, proxy

    def _test_resources(self, creds, proxy):
        session = auth_vk_api(SessionData(creds=creds, proxy=proxy), self.errors_handler, session_id=-999)
        if session is None:
            print(f"changing {proxy.obj_id} proxy status to worked out")
            proxy.status = RESOURCE_WORKED_OUT_STATUS
            return False
        try:
            res = session.method("groups.get", values={"user_id": 1})
            res = session.method("friends.get", values={"user_id": 1})
            print("Test succeeded")
            return True
        except exceptions.ApiError as e:
            print("Test failed, error:", e)
            return False
