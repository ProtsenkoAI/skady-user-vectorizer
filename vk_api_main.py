import os

from suvec.vk_api_impl.crawl_runner_with_checkpoints import VkCrawlRunnerWithCheckpoints
from suvec.vk_api_impl.session.records_managing.resources_import import WebshareFileProxyImporter, VkFileCredsImporter
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.vk_api_impl.session.records_managing.records_storing.serializers import ProxyRecordsSerializer, \
    CredsRecordsSerializer


def run():
    events_tracker = TerminalEventsTracker(log_pth="../logs.txt", report_every_responses_nb=300)

    base_dir = "/home/gldsn/Projects/skady-user-vectorizer/resources/"
    proxies_save_pth = os.path.join(base_dir, "proxies.json")
    creds_save_pth = os.path.join(base_dir, "creds.json")

    proxy_storage = ProxyStorage(proxies_save_pth, ProxyRecordsSerializer())
    creds_storage = CredsStorage(creds_save_pth, CredsRecordsSerializer())

    _import_proxy_and_creds_from_files(proxy_storage, creds_storage, base_dir)

    runner = VkCrawlRunnerWithCheckpoints(
        start_user_id="213167272",
        data_resume_checkpoint_save_pth=os.path.join(base_dir, "checkpoints/data_checkpoint.json"),
        tracker=events_tracker,
        proxy_storage=proxy_storage,
        creds_storage=creds_storage,
        requester_checkpoints_path=os.path.join(base_dir, "checkpoints/requester_checkpoint.json"),
        requester_max_requests_per_crawl_loop=50,
        long_term_save_pth=os.path.join(base_dir, "parsed_data.json")
    )
    runner.run()


def _import_proxy_and_creds_from_files(proxy_storage, creds_storage, base_dir):
    ...
    ### Turn on only once with new files, because can create duplicates
    # proxy_importer = WebshareFileProxyImporter(
    #     path_to_resources=os.path.join(base_dir, "session/webshare_250_proxies.txt"),
    #     min_obj_id=proxy_storage.get_next_record_id()
    # )
    # proxy_importer.import_records(proxy_storage)
    #
    # creds_importer = VkFileCredsImporter(
    #     path_to_resources=os.path.join(base_dir, "session/vk_accounts.txt"),
    #     min_obj_id=creds_storage.get_next_record_id()
    # )
    # creds_importer.import_records(creds_storage)


if __name__ == "__main__":
    run()
