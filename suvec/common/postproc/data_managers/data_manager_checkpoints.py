import json
import shutil
import os

from .ram_data_manager import RAMDataManager
import signal


class DataManagerCheckpointer:
    # TODO: refactor
    # TODO: refactor secure-file-writing
    """Wrapper that adds periodic saving of parsed data and ability to load from save
    """
    def __init__(self, resume_checkpoint_save_pth: str, long_term_backup_path: str,
                 long_term_save_path: str, events_tracker):
        self.save_pth = resume_checkpoint_save_pth
        self.long_term_save_pth = long_term_save_path
        self.tracker = events_tracker
        self.cnt_saved_data = 0  # breaks in case of resuming from non-empty long term data storage
        self.backup_parsed_every = 10 ** 5
        self.long_term_backup_path = long_term_backup_path

    def save_checkpoint(self, data_manager: RAMDataManager):
        self._dump_long_term(data_manager)

        saved_data = data_manager.get_data()
        print("Number of unpaired users in data_manager checkpoint:", len(saved_data))

        self._need_to_stop = False
        signal.signal(signal.SIGTERM, self._wait_till_write_end)
        with open(self.save_pth, "w") as f:
            json.dump(saved_data, f)

        if self._need_to_stop:
            signal.raise_signal(signal.SIGTERM)

    def _wait_till_write_end(self):
        self._need_to_stop = True

    def _dump_long_term(self, data_manager: RAMDataManager):
        data = data_manager.take_fully_parsed_users()
        for user, _ in data.items():
            data_manager.delete_user(user)

        total_groups = self._cnt_groups(data)
        self.tracker.report_long_term_data_stats(len(data) + self.cnt_saved_data, total_groups)
        self.cnt_saved_data += len(data)

        self._need_to_stop = False
        signal.signal(signal.SIGTERM, self._wait_till_write_end)
        with open(self.long_term_save_pth, "a") as f:
            for user, user_data in data.items():
                saved_line = json.dumps({"user_id": user, "data": user_data})
                f.write(saved_line + "\n")
        if self._need_to_stop:
            signal.raise_signal(signal.SIGTERM)

        saved_data_exceeds_backup_point = (self.cnt_saved_data // self.backup_parsed_every >
                                           (self.cnt_saved_data - len(data)) // self.backup_parsed_every)
        if saved_data_exceeds_backup_point:
            self._backup_long_term()

    def _backup_long_term(self):
        shutil.copy(self.long_term_save_pth, self.long_term_backup_path)

    @staticmethod
    def _cnt_groups(data):
        return sum([len(user_data["groups"]) for user_data in data.values()])

    def load_checkpoint(self, data_manager: RAMDataManager):
        if os.path.isfile(self.save_pth):
            with open(self.save_pth) as f:
                data = json.load(f)
            data_manager.set_data(data)
        else:
            with open(self.save_pth, "w") as f:
                default_val = {}
                json.dump(default_val, f)
