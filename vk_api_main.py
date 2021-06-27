import utils
from suvec.vk_api_impl.crawl_runner_with_checkpoints import VkCrawlRunnerWithCheckpoints
from suvec.common.events_tracking.terminal_events_tracker import TerminalEventsTracker
from suvec.vk_api_impl.session.records_managing.records_storing import ProxyStorage, CredsStorage


def run():
    events_tracker = TerminalEventsTracker(log_pth="../logs.txt", report_every_responses_nb=1000)

    settings_path = "./settings.json"
    proxies_save_pth, creds_save_pth = utils.get_proxy_and_creds_paths(settings_path)
    checkp_data, checkp_requester = utils.get_data_requester_checkpoint_paths(settings_path)
    result_file = utils.get_result_path(settings_path)
    backups_path = utils.get_backups_path(settings_path)

    proxy_storage = ProxyStorage(proxies_save_pth)
    creds_storage = CredsStorage(creds_save_pth)

    runner = VkCrawlRunnerWithCheckpoints(
        start_user_id=142478661,
        data_resume_checkpoint_save_pth=checkp_data,
        tracker=events_tracker,
        proxy_storage=proxy_storage,
        creds_storage=creds_storage,
        requester_checkpoints_path=checkp_requester,
        requester_max_requests_per_loop=4000,
        long_term_save_pth=result_file,
        data_backup_path=str(backups_path / "parsed_backup.jsonl"),
        loops_per_checkpoint=3,
        use_async=True,
        nb_sessions=8,
        dmp_long_term_steps=2000
    )
    runner.run()


if __name__ == "__main__":
    run()
