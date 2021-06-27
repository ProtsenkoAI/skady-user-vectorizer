import unittest
import shutil

import utils
from suvec.vk_api_impl.session.sessions_containers import SessionsContainer
from suvec.vk_api_impl.session.session_manager_impl import SessionManagerImpl
from suvec.vk_api_impl.session.records_managing import ProxyManager, CredsManager
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.common.events_tracking import TerminalEventsTracker
from suvec.vk_api_impl.errors_handler import VkApiErrorsHandler

settings_path = "./settings.json"
proxies_save_pth, creds_save_pth = utils.get_proxy_and_creds_paths(settings_path)

testing_dir = utils.get_resources_path(settings_path) / "testing"
testing_proxies_pth = testing_dir / "proxies.json"
testing_creds_pth = testing_dir / "creds.json"


class TestSessionManagerImpl(unittest.TestCase):
    def setUp(self):
        shutil.copy(proxies_save_pth, testing_proxies_pth)
        shutil.copy(creds_save_pth, testing_creds_pth)

    def test_allocate_multiple_sessions(self):
        """Allocates sessions to multiple containers and checks they don't intersect
        """
        session_manager = self._create()
        cont1, cont2 = SessionsContainer(), SessionsContainer()
        session_manager.allocate_sessions(2, cont1)
        session_manager.allocate_sessions(3, cont2)

        sessions1 = cont1.get()
        sessions2 = cont2.get()

        for session in sessions1:
            self.assertNotIn(session, sessions2)

    def test_removes_bad_session(self):
        """Marks sessions as bad and checks that they were removed from container"""
        session_manager = self._create(tester_fill_value=False)
        cont = SessionsContainer()
        session_manager.allocate_sessions(2, cont)
        bad_sessions_with_ids = cont.get().copy()
        for session_id, session in bad_sessions_with_ids:
            if session_id % 2:
                session_manager.session_error_occurred(session_id)
            else:
                session_manager.bad_password(session_id)

        new_sessions = cont.get()
        _, bad_sessions = zip(*bad_sessions_with_ids)
        for _, session in new_sessions:
            self.assertNotIn(session, bad_sessions)

    def test_reuses_resource_if_test_succeed(self):
        """Checks that if resource test passes successfully then reuses this resource"""
        session_manager = self._create(tester_fill_value=True)
        cont = SessionsContainer()
        session_manager.allocate_sessions(1, cont)

        bad_session_id, bad_session = cont.get().copy()[0]
        session_manager.session_error_occurred(bad_session_id)

        new_session_id, new_session = cont.get().copy()[0]
        self.assertEqual(new_session, bad_session)

    def test_can_reuse_worked_out(self):
        """Marks resources as bad, but then tests them and marks as good again. This tests checks that
        session manager can retrieve same resources infinitely and tries to check them, thus reusing old resources in
        production"""
        session_manager = self._create(tester_fill_value=True)
        container = SessionsContainer()
        session_manager.allocate_sessions(1, container)

        for _ in range(500):
            sess_id, _ = container.get()[0]
            session_manager.session_error_occurred(sess_id)

    def test_stops_add_sessions_if_have_no_proxies(self):
        """Marking all proxies as bad and check that at some moment raises error"""
        session_manager = self._create(tester_fill_value=True)
        container = SessionsContainer()
        session_manager.allocate_sessions(1, container)

        with self.assertRaises(RuntimeError):
            for _ in range(500):
                sess_id, _ = container.get()[0]
                session_manager.proxy_error_occurred(sess_id)

    def test_allocated_sessions_are_unique(self):
        nb_sessions = 8

        session_manager = self._create()
        container = SessionsContainer()
        session_manager.allocate_sessions(nb_sessions, container)

        sessions = container.get()
        met_sessions_data = []

        for session_id, session in sessions:
            sess_data = session.proxy.proxy, session.creds.creds
            self.assertNotIn(sess_data, met_sessions_data)
            met_sessions_data.append(sess_data)

    def _create(self, tester_fill_value=False):
        # TODO: maybe we can create session_manager easier? It becomes real problem to create all this stuff
        proxies_storage = ProxyStorage(str(testing_proxies_pth))
        creds_storage = CredsStorage(str(testing_creds_pth))
        tracker = TerminalEventsTracker(log_pth="./test_logs.txt", report_every_responses_nb=10 ** 9)

        proxies_manager = ProxyManager(proxies_storage, tracker)
        creds_manager = CredsManager(creds_storage, tracker)
        errors_handler = VkApiErrorsHandler(events_tracker=tracker)
        return SessionManagerImpl(errors_handler=errors_handler, proxy_manager=proxies_manager,
                                  creds_manager=creds_manager, tester=MockTester(tester_fill_value))


class MockTester:
    def __init__(self, fill_val):
        self.fill_val = fill_val

    def get_container(self):
        return SessionsContainer()

    def test_proxy(self, *args, **kwargs):
        return self.fill_val

    def test_creds(self, *args, **kwargs):
        return self.fill_val
