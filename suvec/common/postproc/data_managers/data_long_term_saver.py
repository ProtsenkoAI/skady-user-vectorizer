from typing import Dict, Any
import json
import shutil

from .data_manager import UsersData
from suvec.common.utils import shield_from_termination

UserId = int
UserData = Dict[str, Any]


class DataLongTermSaver:
    # TODO: add abstract classes, refactor etc.
    def __init__(self, save_pth: str, backup_save_pth: str, backup_parsed_every: int = 3 * 10 ** 4):
        self.save_pth = save_pth
        self.backup_save_pth = backup_save_pth
        self.cnt_saved_data = 0
        self.backup_parsed_every = backup_parsed_every

    def save(self, data: UsersData):
        self._write_long_term(data)

        saved_data_exceeds_backup_point = (self.cnt_saved_data // self.backup_parsed_every >
                                           (self.cnt_saved_data - len(data)) // self.backup_parsed_every)
        if saved_data_exceeds_backup_point:
            self._backup_long_term()

    @shield_from_termination
    def _write_long_term(self, data: UsersData):
        with open(self.save_pth, "a") as f:
            for user, user_data in data.items():
                saved_line = json.dumps({"user_id": user, "data": user_data})
                f.write(saved_line + "\n")
                self.cnt_saved_data += 1

    @shield_from_termination
    def _backup_long_term(self):
        shutil.copy(self.save_pth, self.backup_save_pth)
