from suvec.vk_api_impl.crawl_runner import VkApiCrawlRunner
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.vk_api_impl.session.records_managing.records_storing.serializers import ProxyRecordsSerializer, CredsRecordsSerializer


def run():
    events_tracker = TerminalEventsTracker(log_pth="../logs.txt", report_every_responses_nb=300)

    proxies_save_pth = "../resources/proxies.json"
    creds_save_pth = "../resources/creds.json"
    proxy_storage = ProxyStorage(proxies_save_pth, ProxyRecordsSerializer())
    creds_storage = CredsStorage(creds_save_pth, CredsRecordsSerializer())

    runner = VkApiCrawlRunner(start_user_id="213167272",
                              parse_res_save_pth="/home/gldsn/Projects/skady-user-vectorizer/resources/checkpoint.json",
                              tracker=events_tracker,
                              proxy_storage=proxy_storage,
                              creds_storage=creds_storage,
                              save_every_n_users_parsed=50
                              )
    runner.run()


if __name__ == "__main__":
    run()
