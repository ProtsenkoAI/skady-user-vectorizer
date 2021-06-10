from .crawl_runner import VkApiCrawlRunner
from suvec.common.postproc.data_managers.data_manager_checkpoints import DataManagerCheckpointer
from suvec.common.requesting.requester_checkpointer import RequesterCheckpointer


class VkCrawlRunnerWithCheckpoints(VkApiCrawlRunner):
    def __init__(self, *args, data_resume_checkpoint_save_pth: str, data_backup_path: str, long_term_save_pth: str,
                 requester_checkpoints_path: str, loops_per_checkpoint: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_checkpointer = DataManagerCheckpointer(data_resume_checkpoint_save_pth, data_backup_path,
                                                         long_term_save_pth, self.events_tracker)
        self.requester_checkpointer = RequesterCheckpointer(requester_checkpoints_path)

        self.requester_checkpointer.load_checkpoint(self.requester)
        self.data_checkpointer.load_checkpoint(self.data_manager)
        self.loop_idx = 0
        self.loops_per_checkpoint = loops_per_checkpoint

    def end_loop(self):

        super().end_loop()
        if self.loop_idx % self.loops_per_checkpoint == 0:
            self.requester_checkpointer.save_checkpoint(self.requester)
            self.data_checkpointer.save_checkpoint(self.data_manager)

        self.loop_idx += 1
