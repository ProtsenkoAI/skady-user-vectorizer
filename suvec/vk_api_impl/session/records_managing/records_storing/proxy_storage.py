from .storage import AuthRecordsStorage
from ..records import ProxyRecord
from ..session_types import Proxy


class ProxyStorage(AuthRecordsStorage):
    def replace_proxy(self, record: ProxyRecord, new_address: str, new_protocols_str: str):
        new_protocols = list(new_protocols_str.split(","))
        new_proxy = Proxy(new_address, new_protocols)
        record_in_storage = self.get_record_by_id(record.obj_id)
        record_in_storage.proxy = new_proxy
