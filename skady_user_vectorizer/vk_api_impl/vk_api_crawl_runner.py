from interfaces import CrawlRunner
from common_components import RAMDataManager, StdOutTracker
from .vk_api_parsed_processor import VkApiParsedProcessor
from interfaces import ParsedEnoughListener, User
from .vk_api_parser import VkApiParser
from .vk_api_pool_executor import VkApiPoolExecutor
from .vk_api_requester import VkApiRequester


class VkApiCrawlRunner(CrawlRunner, ParsedEnoughListener):
    # TODO: check where to place notifier about access errors (currently in parsed processor)
    def __init__(self, start_user_id: str):
        self.requester = VkApiRequester()
        self.executor = VkApiPoolExecutor()
        self.parser = VkApiParser()
        self.parsed_processor = VkApiParsedProcessor(RAMDataManager(), StdOutTracker())

        self.parsed_processor.register_parsed_enough_listener(self)
        self.parsed_processor.register_access_error_listener(self.requester)

        self.start_user = User(id=start_user_id)
        self.continue_crawling = True

    def run(self):
        candidates = [self.start_user]

        while self.continue_crawling:
            self.requester.add_users(candidates)
            requests = self.requester.get_requests()
            responses = self.executor.execute(requests)
            parsed = self.parser.parse(responses)
            self.parsed_processor.process(parsed)

            candidates = self.parsed_processor.get_new_parse_candidates()

    def parsed_enough(self):
        self.continue_crawling = False
