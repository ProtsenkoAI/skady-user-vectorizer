import json
import os

from .ram_data_manager import RAMDataManager
from .types import UsersData


class DataManagerCheckpointer:
    # TODO: refactor
    """Wrapper that adds periodic saving of parsed data and ability to load from save
    """
    def __init__(self, resume_checkpoint_save_pth: str, long_term_save_path: str, events_tracker):
        self.save_pth = resume_checkpoint_save_pth
        self.long_term_save_pth = long_term_save_path
        self.tracker = events_tracker

    def save_checkpoint(self, data_manager: RAMDataManager):
        self._dump_long_term(data_manager)

        saved_data = data_manager.get_data()
        with open(self.save_pth, "w") as f:
            json.dump(saved_data, f)

    def _dump_long_term(self, data_manager: RAMDataManager):
        data = data_manager.take_fully_parsed_users()
        for user, _ in data.items():
            data_manager.delete_user(user)
        if os.path.isfile(self.long_term_save_pth):
            self._update_with_prev_long_term_save(data)

        total_groups = self._cnt_groups(data)
        self.tracker.report_long_term_data_stats(len(data), total_groups)

        with open(self.long_term_save_pth, "w") as f:
            json.dump(data, f)

    def _update_with_prev_long_term_save(self, data: UsersData):
        with open(self.long_term_save_pth) as f:
            prev_long_term_data = json.load(f)
        data.update(prev_long_term_data)

    def _cnt_groups(self, data):
        return sum([len(user_data["groups"]) for user_data in data.values()])

    def load_checkpoint(self, data_manager: RAMDataManager):
        if os.path.isfile(self.save_pth):
            with open(self.save_pth) as f:
                data = json.load(f)

            data_manager.set_data(data)
        else:
            RuntimeError("There's no checkpoint, can't load")
