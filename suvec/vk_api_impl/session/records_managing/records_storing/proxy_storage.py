from .storage import AuthRecordsStorage
from ..records import ProxyRecord
from ..session_types import Proxy
from .serializers import ProxyRecordsSerializer


class ProxyStorage(AuthRecordsStorage):
    def __init__(self, save_pth: str):
        super().__init__(save_pth, ProxyRecordsSerializer())

    def replace_proxy(self, record: ProxyRecord, new_address: str):
        new_proxy = Proxy(new_address)
        record.proxy = new_proxy
        self.dump_records()

    def prepare_record(self, record: ProxyRecord):
        return record.proxy
