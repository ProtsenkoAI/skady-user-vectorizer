import unittest
import shutil

import utils
from suvec.vk_api_impl.session.session_units import SessionUnit
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

    def test_unique_sessions(self):
        """Allocates sessions to multiple containers and checks they don't intersect
        """
        # TODO: move to SessionUnit tests
        session_manager = self._create()
        n_units = 10
        unit_sessions = [SessionUnit(session_manager).get() for _ in range(n_units)]
        creds, proxies = zip(*unit_sessions)
        self.assertTrue(len(set(unit_sessions)) == n_units == len(set(creds)) == len(set(proxies)))

    def test_allocated_sessions_are_unique(self):
        """Marks sessions as bad and checks that they will not be returned again"""
        session_manager = self._create()
        unit = SessionUnit(session_manager)
        old_bad_sessions = []
        for _ in range(5):
            old_bad_sessions.append(unit.get())
            unit.access_error_occurred()

            new_session = unit.get()
            self.assertNotIn(new_session, old_bad_sessions)

    def test_stops_add_sessions_if_have_no_proxies(self):
        """Marking all proxies as bad and check that at some moment raises error"""
        session_manager = self._create()
        unit = SessionUnit(session_manager)

        with self.assertRaises(StopIteration):
            for _ in range(500):
                unit.access_error_occurred()

    def _create(self):
        # TODO: maybe we can create session_manager easier? It becomes real problem to create all this stuff
        proxies_storage = ProxyStorage(str(testing_proxies_pth))
        creds_storage = CredsStorage(str(testing_creds_pth))
        tracker = TerminalEventsTracker(log_pth="./test_logs.txt", report_every_responses_nb=10 ** 9)

        proxies_manager = ProxyManager(proxies_storage, tracker)
        creds_manager = CredsManager(creds_storage, tracker)
        errors_handler = VkApiErrorsHandler(events_tracker=tracker)
        return SessionManagerImpl(proxy_manager=proxies_manager, creds_manager=creds_manager)
