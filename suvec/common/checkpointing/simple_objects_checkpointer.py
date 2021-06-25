from typing import Any
import json
import os

from suvec.common.utils import shield_from_termination


class SimpleObjectsCheckpointer:
    Jsonable = Any  # any json-serializable object

    def __init__(self, save_pth: str):
        self.save_pth = save_pth

    @shield_from_termination
    def save_checkpoint(self, checkp_data: Jsonable):
        with open(self.save_pth, "w") as f:
            json.dump(checkp_data, f)

    def load_checkpoint(self):
        if os.path.isfile(self.save_pth):
            with open(self.save_pth) as f:
                data = json.load(f)
            return data
