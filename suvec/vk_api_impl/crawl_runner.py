import time

from suvec.common.crawling import CrawlRunner
from suvec.common.top_level_types import User
from .crawl_components import CrawlComps


class VkApiCrawlRunner(CrawlRunner):
    # IMPROVE: If performance will become a problem, will need to refactor from single-user methods to batch-of-users

    # IMPROVE: need integration unit_tests with crawl runner and mock components to test that all listen/notify
    #   connections are set up and work properly
    def __init__(self, start_user_id: int, comps: CrawlComps):
        comps.success_request_notifier.register_request_success_listener(comps.requester)
        comps.parsed_processor.add_process_success_hook(comps.success_request_notifier)
        comps.errors_handler.register_user_unrelated_listener(comps.requester)

        self.continue_crawling = True
        self.has_to_break_parsing = False
        self.candidates = [User(id=start_user_id)]

        self.comps = comps

    def run(self):
        comps = self.comps
        while self.continue_crawling:
            comps.requester.add_users(self.candidates)
            print("added users")
            requests = comps.requester.get_requests()
            print("requests", len(requests))
            start_execute = time.time()
            parsed = comps.executor.execute(requests)
            print("time to get responses", time.time() - start_execute)
            print("responses", len(parsed))

            process_start_time = time.time()
            for parsed_response in parsed:
                comps.parsed_processor.process(parsed_response)
            process_time = time.time() - process_start_time
            print("time to process", process_time)

            self.candidates = comps.parsed_processor.get_new_parse_candidates()
            comps.tracker.state_report()
            self.end_loop()

    def end_loop(self):
        pass

    def stop(self):
        self.continue_crawling = False
