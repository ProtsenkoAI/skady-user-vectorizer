from impl.callback_requester import CallbackRequester
from impl.scrapy_parser import ScrapyParser
from impl.parsed_processor_impl import ParsedProcessorImpl
from impl.scrapy_requests_creator import ScrapyRequestsCreator
from impl.ram_data_manager import RAMDataManager
from impl.stdout_tracker import StdOutTracker
from impl.spider import Spider
from interfaces import Credentials, User
from impl.utils import run_crawl
import util


if __name__ == "__main__":
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
