from .crawl_runner import VkApiCrawlRunner
from suvec.common.checkpointing.simple_objects_checkpointer import SimpleObjectsCheckpointer
from suvec.vk_api_impl.session.session_manager_impl import OutOfRecords


class VkCrawlRunnerWithCheckpoints(VkApiCrawlRunner):
    # TODO: check that when have no records and exiting form pool executor with OutOfResources, it saves changes and
    #   exits till next day
    def __init__(self, *args, data_resume_checkpoint_save_pth: str,
                 requester_checkpoints_path: str, loops_per_checkpoint: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_checkpointer = SimpleObjectsCheckpointer(data_resume_checkpoint_save_pth)
        self.requester_checkpointer = SimpleObjectsCheckpointer(requester_checkpoints_path)

        data_checkpoint = self.data_checkpointer.load_checkpoint()

        if data_checkpoint is not None:
            self.comps.data_manager.load_checkpoint(data_checkpoint)
        requester_checkpoint = self.requester_checkpointer.load_checkpoint()
        if requester_checkpoint is not None:
            self.comps.requester.load_checkpoint(requester_checkpoint)

        self.loop_idx = 0
        self.loops_per_checkpoint = loops_per_checkpoint

    def end_loop(self):
        if self.loop_idx % self.loops_per_checkpoint == 0:
            self._make_checkpoint()

        self.loop_idx += 1

    def run(self):
        try:
            super().run()
        except OutOfRecords:
            self._make_checkpoint()

    def _make_checkpoint(self):
        self.requester_checkpointer.save_checkpoint(self.comps.requester.get_checkpoint())
        self.data_checkpointer.save_checkpoint(self.comps.data_manager.get_checkpoint())