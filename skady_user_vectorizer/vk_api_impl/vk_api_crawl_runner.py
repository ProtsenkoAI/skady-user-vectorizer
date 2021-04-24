from interfaces import CrawlRunner
from common_components import RAMDataManager, StdOutTracker
from .vk_api_parsed_processor import VkApiParsedProcessor
from interfaces import ParsedEnoughListener, User
from .vk_api_parser import VkApiParser
from .vk_api_pool_executor import VkApiPoolExecutor
from .vk_api_requester import VkApiRequester
from .session_manager import SessionManager
from .util import read_proxies_and_creds


class VkApiCrawlRunner(CrawlRunner, ParsedEnoughListener):
    def __init__(self, start_user_id: str, path_to_proxies: str, path_to_creds: str):
        self.requester = VkApiRequester()

        proxies, creds = read_proxies_and_creds(path_to_proxies, path_to_creds)
        session_manager = SessionManager(proxies=proxies, credentials=creds)
        self.executor = VkApiPoolExecutor(session_manager=session_manager)

        self.parser = VkApiParser()
        self.parsed_processor = VkApiParsedProcessor(RAMDataManager(), StdOutTracker())

        self.parsed_processor.register_parsed_enough_listener(self)
        self.parsed_processor.register_access_error_listener(self.executor)

        self.start_user = User(id=start_user_id)
        self.continue_crawling = True

    def run(self):
        candidates = [self.start_user]

        while self.continue_crawling:
            self.requester.add_users(candidates)
            requests = self.requester.get_requests()
            responses = self.executor.execute(requests)
            parsed = [resp.parse(self.parser) for resp in responses]
            for parsed_response in parsed:
                self.parsed_processor.process(parsed_response)

            candidates = self.parsed_processor.get_new_parse_candidates()

    def parsed_enough(self):
        self.continue_crawling = False
