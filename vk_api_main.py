from suvec.vk_api_impl.crawl_runner import VkApiCrawlRunner
from suvec.common.events_tracker import LogEventsTracker
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.vk_api_impl.session.records_managing.records_storing.serializers import ProxyRecordsSerializer, CredsRecordsSerializer


def run():
    events_tracker = LogEventsTracker(log_pth="../logs.txt", report_every_responses_nb=300)

    proxies_save_pth = "../resources/proxies.json"
    creds_save_pth = "../resources/creds.json"
    proxy_storage = ProxyStorage(proxies_save_pth, ProxyRecordsSerializer())
    creds_storage = CredsStorage(creds_save_pth, CredsRecordsSerializer())

    runner = VkApiCrawlRunner(start_user_id="213167272",
                              parse_res_save_pth="../checkpoint.json",
                              events_tracker=events_tracker,
                              proxy_storage=proxy_storage,
                              creds_storage=creds_storage
                              )
    runner.run()


if __name__ == "__main__":
    run()
