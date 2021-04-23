from common_components import CallbackRequester
from scrapy_impl.scrapy_parser import ScrapyParser
from common_components import ParsedProcessorImpl
from scrapy_impl.scrapy_requests_creator import ScrapyRequestsCreator
from common_components import RAMDataManager
from common_components import StdOutTracker
from scrapy_impl.spider import Spider
from interfaces import Credentials, User
from scrapy_impl.utils import run_crawl
import util


def run():
    config = util.read_config()
    # just instantiate spider with all needed objects
    parser = ScrapyParser()
    data_manager = RAMDataManager()
    stdout_tracker = StdOutTracker(print_every=30)
    parsed_processor = ParsedProcessorImpl(data_manager=data_manager, progress_tracker=stdout_tracker)
    creds = Credentials(config["creds"]["email"], config["creds"]["password"])
    requests_creator = ScrapyRequestsCreator(creds=creds)
    requester = CallbackRequester(parser, parsed_processor, requests_creator)
    requests_creator.set_get_requests_callable(requester.get_requests)

    start_user = User(id="371492632")
    run_crawl(Spider, requester, start_user)


if __name__ == "__main__":
    run()
