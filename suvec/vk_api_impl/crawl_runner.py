import time

from suvec.common.crawling import CrawlRunner
from suvec.common.postproc.data_managers.ram_data_manager_with_checkpoints import RAMDataManagerWithCheckpoints
from suvec.common.postproc import SessionSwitchingParsedProcessor
from suvec.common.top_level_types import User
from suvec.common.listen_notify import ParsedEnoughListener
from suvec.common.requesting.requester_impl import RequesterImpl
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from .session.records_managing.terminal_out_of_records import TerminalOutOfProxy, TerminalOutOfCreds

from .executing.pool_executor import VkApiPoolExecutor
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from .executing.responses_factory import VkApiResponsesFactory
from .requesting import VkApiRequestsCreator
from .errors_handler import VkApiErrorsHandler
from .session.records_managing.proxy_manager import ProxyManager
from .session.records_managing.creds_manager import CredsManager
from .session import SessionManager


class VkApiCrawlRunner(CrawlRunner, ParsedEnoughListener):
    # TODO: If performance will become a problem, will need to refactor from single-user methods to batch-of-users
    #   methods and use multithreading
    def __init__(self, start_user_id: str, proxy_storage: ProxyStorage, creds_storage: CredsStorage,
                 parse_res_save_pth: str, logs_pth: str = "../logs.txt",
                 tracker=None, requester_max_requests_per_crawl_loop=1000,
                 tracker_response_freq=500, session_request_limit=30000,
                 save_every_n_users_parsed=1000, access_resource_reload_hours=24,
                 max_users=10**7):

        if tracker is None:
            tracker = TerminalEventsTracker(log_pth=logs_pth, report_every_responses_nb=tracker_response_freq)

        self.events_tracker = tracker
        CrawlRunner.__init__(self, tracker=tracker)

        responses_factory = VkApiResponsesFactory()
        requests_creator = VkApiRequestsCreator(responses_factory=responses_factory)
        self.requester = RequesterImpl(requests_creator,
                                       max_requests_per_type_per_call=requester_max_requests_per_crawl_loop)

        errors_handler = VkApiErrorsHandler(tracker)

        out_of_proxy_handler = TerminalOutOfProxy()
        out_of_creds_handler = TerminalOutOfCreds()
        proxy_manager = ProxyManager(proxy_storage, tracker, out_of_proxy_handler,
                                     hours_for_resource_reload=access_resource_reload_hours)
        creds_manager = CredsManager(creds_storage, tracker, out_of_creds_handler,
                                     hours_for_resource_reload=access_resource_reload_hours)

        session_manager = SessionManager(errors_handler, proxy_manager, creds_manager)
        self.executor = VkApiPoolExecutor(session_manager=session_manager)

        self.data_manager = RAMDataManagerWithCheckpoints(save_pth=parse_res_save_pth,
                                                          save_every_n_users=save_every_n_users_parsed)
        # TODO: processor shouldn't count requests, move it to requester
        self.parsed_processor = SessionSwitchingParsedProcessor(self.data_manager, tracker,
                                                                errors_handler=errors_handler,
                                                                requests_per_session_limit=session_request_limit,
                                                                max_users=max_users)

        self.parsed_processor.register_parsed_enough_listener(self)
        errors_handler.register_access_error_listener(self.executor)
        errors_handler.register_bad_password_listener(session_manager)

        self.start_user = User(id=start_user_id)
        self.continue_crawling = True

    def run(self):
        candidates = [self.start_user]

        while self.continue_crawling:
            self.events_tracker.loop_started()
            self.requester.add_users(candidates)
            print("added users")
            requests = self.requester.get_requests()
            print("requests", len(requests))
            start_execute = time.time()
            responses = self.executor.execute(requests)
            print("time to get responses", time.time() - start_execute)
            print("responses", len(responses))
            parsed = [resp.parse() for resp in responses]
            print("parsed", len(parsed))
            for parsed_response in parsed:
                self.parsed_processor.process(parsed_response)

            candidates = self.parsed_processor.get_new_parse_candidates()
            self.events_tracker.loop_ended()

    def parsed_enough(self):
        self.continue_crawling = False

    def stop(self):
        self.continue_crawling = False
