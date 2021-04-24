from interfaces import CrawlRunner
from .callback_requester import CallbackRequester
from scrapy_impl.scrapy_parser import ScrapyParser
from common_components import ParsedProcessorImpl
from scrapy_impl.scrapy_requests_creator import ScrapyRequestsCreator
from common_components import RAMDataManager
from common_components import StdOutTracker
from interfaces import Credentials, User
from . import utils
from .spider import Spider


class ScrapyVkCrawlRunner(CrawlRunner):
    def __init__(self, config, user_id: str, tracker_print_every: int = 30):
        parser = ScrapyParser()
        data_manager = RAMDataManager()
        stdout_tracker = StdOutTracker(print_every=tracker_print_every)
        parsed_processor = ParsedProcessorImpl(data_manager=data_manager, progress_tracker=stdout_tracker)
        creds = Credentials(config["creds"]["email"], config["creds"]["password"])
        requests_creator = ScrapyRequestsCreator(creds=creds)
        self.requester = CallbackRequester(parser, parsed_processor, requests_creator)
        requests_creator.set_get_requests_callable(self.requester.get_requests)

        self.start_user = User(id=user_id)

    def run(self):
        utils.run_crawl(Spider, self.requester, self.start_user)
