from interfaces import CrawlRunner
from common_components import RAMDataManager
from .vk_api_parsed_processor import VkApiParsedProcessor
from interfaces import ParsedEnoughListener, User
from vk_api_impl.vk_api_specific.vk_api_pool_executor import VkApiPoolExecutor
from .vk_api_requester import VkApiRequester
from .requests_creator import VkApiRequestsCreator
from .events_tracker import EventsTracker
from .session import ProxyManager, CredsManager
from .session import AuthRecordsStorage, ProxyRecordsSerializer, CredsRecordsSerializer
from vk_api_impl.vk_api_specific.session_manager import SessionManager
from .vk_api_specific.api_errors_handler import VkApiErrorsHandler
from vk_api_impl.vk_api_responses_factory import VkApiResponsesFactory
import time


class VkApiCrawlRunner(CrawlRunner, ParsedEnoughListener):
    def __init__(self, start_user_id: str, proxies_save_pth: str, creds_save_pth: str,
                 logs_pth: str = "./logs.txt"):
        events_tracker = EventsTracker(log_pth=logs_pth, report_every_responses_nb=100)
        responses_factory = VkApiResponsesFactory()
        requests_creator = VkApiRequestsCreator(responses_factory=responses_factory)
        self.requester = VkApiRequester(requests_creator)

        errors_handler = VkApiErrorsHandler(events_tracker)
        # proxy_creds_storage = ProxyAndCredsStorage(path_to_proxies_and_creds)
        proxy_storage = AuthRecordsStorage(proxies_save_pth, ProxyRecordsSerializer())
        creds_storage = AuthRecordsStorage(creds_save_pth, CredsRecordsSerializer())

        proxy_manager = ProxyManager(proxy_storage, events_tracker)
        creds_manager = CredsManager(creds_storage, events_tracker)

        session_manager = SessionManager(errors_handler, proxy_manager, creds_manager)
        errors_handler.register_bad_password_listener(session_manager)
        self.executor = VkApiPoolExecutor(session_manager=session_manager)

        self.parsed_processor = VkApiParsedProcessor(RAMDataManager(), events_tracker, errors_handler=errors_handler)

        self.parsed_processor.register_parsed_enough_listener(self)
        self.parsed_processor.register_access_error_listener(self.executor)

        self.start_user = User(id=start_user_id)
        self.continue_crawling = True

    def run(self):
        candidates = [self.start_user]

        while self.continue_crawling:
            self.requester.add_users(candidates)
            print("added users")
            requests = self.requester.get_requests()
            print("requests", len(requests))
            responses = self.executor.execute(requests)
            print("responses", len(responses))
            parsed = [resp.parse() for resp in responses]
            print("parsed", len(parsed))
            for parsed_response in parsed:
                self.parsed_processor.process(parsed_response)

            candidates = self.parsed_processor.get_new_parse_candidates()

            time.sleep(5)  # TODO: turn off

    def parsed_enough(self):
        self.continue_crawling = False
