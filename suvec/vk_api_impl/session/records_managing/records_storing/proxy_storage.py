from .storage import AuthRecordsStorage
from ..records import ProxyRecord
from ..session_types import Proxy


class ProxyStorage(AuthRecordsStorage):
    def replace_proxy(self, record: ProxyRecord, new_address: str):
        new_proxy = Proxy(new_address)
        record.proxy = new_proxy
        self.dump_records()

    def prepare_record(self, record: ProxyRecord):
        return record.proxy
