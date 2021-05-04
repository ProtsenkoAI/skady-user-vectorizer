import json
import os

from .ram_data_manager import RAMDataManager


class DataManagerCheckpointer:
    # TODO: when saving checkpoint, have to delete fully saved users from RAM
    """Wrapper that adds periodic saving of parsed data and ability to load from save
    """
    def __init__(self, save_pth: str):
        self.save_pth = save_pth

    def save_checkpoint(self, data_manager: RAMDataManager):
        saved_data = data_manager.get_data()

        with open(self.save_pth, "w") as f:
            json.dump(saved_data, f)

    def load_checkpoint(self, data_manager: RAMDataManager):
        if os.path.isfile(self.save_pth):
            with open(self.save_pth) as f:
                data = json.load(f)

            data_manager.set_data(data)
