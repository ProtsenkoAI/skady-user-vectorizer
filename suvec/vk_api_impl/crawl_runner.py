import time

from suvec.common.crawling import CrawlRunner
from suvec.common.postproc.data_managers.ram_data_manager import RAMDataManager
from suvec.common.postproc import ParsedProcessorWithHooks
from suvec.common.postproc.processor_hooks import HookSuccessParseNotifier
from suvec.common.top_level_types import User
from suvec.common.requesting import EconomicRequester
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from suvec.common.postproc.data_managers.data_long_term_saver import DataLongTermSaver
from .session.records_managing.terminal_out_of_records import TerminalOutOfProxy, TerminalOutOfCreds


from suvec.common.requesting.requested_users_storage import RequestedUsersFileStorage
from suvec.common.requesting.users_filter import DuplicateUsersFilter
from .executing.pool_executor import VkApiPoolExecutor
from .executing.async_pool_executor import AsyncVkApiPoolExecutor
from .executing.mutli_session_async_pool_executor import MultiSessionAsyncVkApiPoolExecutor
from .executing.responses_factory import AioVkResponsesFactory
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from .executing.responses_factory import VkApiResponsesFactory
from .requesting import VkApiRequestsCreator
from .errors_handler import VkApiErrorsHandler
from .session.records_managing.proxy_manager import ProxyManager
from .session.records_managing.creds_manager import CredsManager
from .session import SessionManagerImpl


class VkApiCrawlRunner(CrawlRunner):
    # TODO: If performance will become a problem, will need to refactor from single-user methods to batch-of-users
    #   methods and use multithreading
    def __init__(self, start_user_id: int, proxy_storage: ProxyStorage, creds_storage: CredsStorage,
                 long_term_save_pth: str, data_backup_path: str,
                 logs_pth: str = "../logs.txt",
                 tracker=None, requester_max_requests_per_loop=10000,
                 tracker_response_freq=500,
                 access_resource_reload_hours=24, use_async=True, nb_sessions=1):

        if tracker is None:
            tracker = TerminalEventsTracker(log_pth=logs_pth, report_every_responses_nb=tracker_response_freq)
        self.tracker = tracker

        self.events_tracker = tracker
        CrawlRunner.__init__(self, tracker=tracker)

        requests_creator = VkApiRequestsCreator()

        friends_req_storage = RequestedUsersFileStorage("./resources/checkpoints/dumped_friends_requests.txt")
        groups_req_storage = RequestedUsersFileStorage("./resources/checkpoints/dumped_groups_requests.txt")
        users_filter = DuplicateUsersFilter()
        self.requester = EconomicRequester(
            requests_creator,
            friends_req_storage=friends_req_storage,
            groups_req_storage=groups_req_storage,
            users_filter=users_filter,
            max_requests_per_call=requester_max_requests_per_loop
        )

        errors_handler = VkApiErrorsHandler(tracker)

        out_of_proxy_handler = TerminalOutOfProxy()
        out_of_creds_handler = TerminalOutOfCreds()
        proxy_manager = ProxyManager(proxy_storage, tracker, out_of_proxy_handler,
                                     hours_for_resource_reload=access_resource_reload_hours)
        creds_manager = CredsManager(creds_storage, tracker, out_of_creds_handler,
                                     hours_for_resource_reload=access_resource_reload_hours)

        self.session_manager = SessionManagerImpl(errors_handler, proxy_manager, creds_manager)
        if use_async:
            responses_factory = AioVkResponsesFactory()
            if nb_sessions == 1:
                self.executor = AsyncVkApiPoolExecutor(self.session_manager, responses_factory)
            else:

                self.executor = MultiSessionAsyncVkApiPoolExecutor(self.session_manager, responses_factory)
        else:
            responses_factory = VkApiResponsesFactory()
            self.executor = VkApiPoolExecutor(self.session_manager, responses_factory)

        long_term_saver = DataLongTermSaver(long_term_save_pth, data_backup_path)
        self.data_manager = RAMDataManager(long_term_saver)
        # TODO: processor shouldn't count requests, move it to requester
        self.parsed_processor = ParsedProcessorWithHooks(self.data_manager, tracker,
                                                         errors_handler=errors_handler)

        success_request_notifier_hook = HookSuccessParseNotifier()
        success_request_notifier_hook.register_request_success_listener(self.requester)

        self.parsed_processor.add_process_success_hook(success_request_notifier_hook)

        errors_handler.register_access_error_listener(self.session_manager)

        errors_handler.register_bad_password_listener(self.session_manager)

        self.continue_crawling = True
        self.has_to_break_parsing = False
        self.candidates = [User(id=start_user_id)]

    def run(self):
        while self.continue_crawling:
            self.requester.add_users(self.candidates)
            print("added users")
            requests = self.requester.get_requests()
            print("requests", len(requests))
            start_execute = time.time()
            parsed = self.executor.execute(requests)
            print("time to get responses", time.time() - start_execute)
            print("responses", len(parsed))

            process_start_time = time.time()
            for parsed_response in parsed:
                self.parsed_processor.process(parsed_response)
            process_time = time.time() - process_start_time
            # TODO: deleted terminatin of processing in case of access error, so need to check performance drop
            print("time to process", process_time)

            self.candidates = self.parsed_processor.get_new_parse_candidates()
            self.tracker.state_report()

    def stop(self):
        self.continue_crawling = False

