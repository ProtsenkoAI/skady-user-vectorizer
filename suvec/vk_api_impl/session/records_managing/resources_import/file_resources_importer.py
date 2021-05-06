from abc import ABC, abstractmethod
from typing import List

from ..records import Record
from ..records_storing.storage import AuthRecordsStorage


class FileResourcesImporter(ABC):
    def __init__(self, path_to_resources: str, min_obj_id: int):
        self.records = self.load_records(path_to_resources, min_obj_id)

    @abstractmethod
    def load_records(self, path: str, start_obj_id: int) -> List[Record]:
        ...

    def import_records(self, records_storage: AuthRecordsStorage):
        for record in self.records:
            records_storage.add_record(record)
