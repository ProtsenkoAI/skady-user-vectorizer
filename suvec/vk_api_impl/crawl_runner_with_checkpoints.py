from .crawl_runner import VkApiCrawlRunner
from suvec.common.checkpointing.simple_objects_checkpointer import SimpleObjectsCheckpointer


class VkCrawlRunnerWithCheckpoints(VkApiCrawlRunner):
    def __init__(self, *args, data_resume_checkpoint_save_pth: str,
                 requester_checkpoints_path: str, loops_per_checkpoint: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_checkpointer = SimpleObjectsCheckpointer(data_resume_checkpoint_save_pth)
        self.requester_checkpointer = SimpleObjectsCheckpointer(requester_checkpoints_path)

        data_checkpoint = self.data_checkpointer.load_checkpoint()

        if data_checkpoint is not None:
            self.data_manager.load_checkpoint(data_checkpoint)
        requester_checkpoint = self.requester_checkpointer.load_checkpoint()
        if requester_checkpoint is not None:
            self.requester.load_checkpoint(requester_checkpoint)

        self.loop_idx = 0
        self.loops_per_checkpoint = loops_per_checkpoint

    def end_loop(self):
        if self.loop_idx % self.loops_per_checkpoint == 0:
            self.requester_checkpointer.save_checkpoint(self.requester.get_checkpoint())
            self.data_checkpointer.save_checkpoint(self.data_manager.get_checkpoint())

        self.loop_idx += 1
