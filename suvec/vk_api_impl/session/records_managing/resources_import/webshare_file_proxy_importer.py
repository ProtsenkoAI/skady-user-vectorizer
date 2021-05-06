from typing import List

from ..records import ProxyRecord
from ..session_types import Proxy
from .file_resources_importer import FileResourcesImporter


class WebshareFileProxyImporter(FileResourcesImporter):
    def load_records(self, path: str, start_obj_id: int) -> List[ProxyRecord]:
        with open(path) as f:
            addresses = f.readlines()

        records = []
        obj_id = start_obj_id
        for address in addresses:
            address = address.strip()
            record = ProxyRecord(proxy=Proxy(address=address, protocols=["http", "https"]), obj_id=obj_id)
            records.append(record)
            obj_id += 1
        return records
