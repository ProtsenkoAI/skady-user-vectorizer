from suvec.vk_api_impl.crawl_runner import VkApiCrawlRunner
from suvec.common.events_tracker import LogEventsTracker


def run():
    events_tracker = LogEventsTracker(log_pth="../logs.txt", report_every_responses_nb=300)

    runner = VkApiCrawlRunner(start_user_id="213167272",
                              proxies_save_pth="../resources/proxies.json",
                              creds_save_pth="../resources/creds.json",
                              parse_res_save_pth="../checkpoint.json",
                              events_tracker=events_tracker,
                              )
    runner.run()


if __name__ == "__main__":
    run()
