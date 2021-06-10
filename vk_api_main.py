import os

from suvec.vk_api_impl.crawl_runner_with_checkpoints import VkCrawlRunnerWithCheckpoints
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage
from suvec.vk_api_impl.session.records_managing.records_storing.serializers import ProxyRecordsSerializer, \
    CredsRecordsSerializer


def run():
    events_tracker = TerminalEventsTracker(log_pth="../logs.txt", report_every_responses_nb=300)

    base_dir = "./resources/"
    proxies_save_pth = os.path.join(base_dir, "proxies.json")
    creds_save_pth = os.path.join(base_dir, "creds.json")

    proxy_storage = ProxyStorage(proxies_save_pth, ProxyRecordsSerializer())
    creds_storage = CredsStorage(creds_save_pth, CredsRecordsSerializer())

    runner = VkCrawlRunnerWithCheckpoints(
        start_user_id="142478661",
        data_resume_checkpoint_save_pth=os.path.join(base_dir, "checkpoints/data_checkpoint.json"),
        tracker=events_tracker,
        proxy_storage=proxy_storage,
        creds_storage=creds_storage,
        requester_checkpoints_path=os.path.join(base_dir, "checkpoints/requester_checkpoint.json"),
        requester_max_requests_per_crawl_loop=1000,
        long_term_save_pth=os.path.join(base_dir, "parsed_data.jsonl")
    )
    runner.run()


if __name__ == "__main__":
    run()
