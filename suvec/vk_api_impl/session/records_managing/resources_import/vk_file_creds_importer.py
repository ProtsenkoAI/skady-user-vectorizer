from typing import List

from ..records import CredsRecord
from ..session_types import Credentials
from .file_resources_importer import FileResourcesImporter


class VkFileCredsImporter(FileResourcesImporter):
    def load_records(self, path: str, start_obj_id: int) -> List[CredsRecord]:
        records = []
        obj_id = start_obj_id
        with open(path) as f:
            lines = f.readlines()

        for line in lines:
            login, password = line.split(":")
            login, password = login.strip(), password.strip()
            creds = Credentials(login, password)
            record = CredsRecord(creds=creds, obj_id=obj_id)
            records.append(record)
            obj_id += 1

        return records
