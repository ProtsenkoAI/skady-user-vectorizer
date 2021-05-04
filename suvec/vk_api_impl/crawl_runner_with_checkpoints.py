import os

from .crawl_runner import VkApiCrawlRunner
from suvec.common.postproc.data_managers.data_manager_checkpoints import DataManagerCheckpointer
from suvec.common.requesting.requester_checkpointer import RequesterCheckpointer


class VkCrawlRunnerWithCheckpoints(VkApiCrawlRunner):
    def __init__(self, *args, parse_res_save_pth: str, requester_checkpoints_path: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_checkpointer = DataManagerCheckpointer(parse_res_save_pth)
        self.requester_checkpointer = RequesterCheckpointer(requester_checkpoints_path)

        self.requester_checkpointer.load_checkpoint(self.requester)
        self.data_checkpointer.load_checkpoint(self.data_manager)

    def end_loop(self):
        super().end_loop()
        self.requester_checkpointer.save_checkpoint(self.requester)
        self.data_checkpointer.save_checkpoint(self.data_manager)
