from .storage import AuthRecordsStorage
from ..records import ProxyRecord
from ..session_types import Proxy


class ProxyStorage(AuthRecordsStorage):
    def replace_proxy(self, record: ProxyRecord, new_address: str):
        new_proxy = Proxy(new_address)
        record_in_storage = self.get_record_by_id(record.obj_id)
        record_in_storage.proxy = new_proxy
        self.dump_records()
