from typing import List

from .proxy_storage_interface import ProxyStorage
from .creds_storage_interface import CredsStorage
from .records import ProxyRecord, CredsRecord


class ProxyAndCredsStorage(ProxyStorage, CredsStorage):

    def get_proxy_records(self) -> List[ProxyRecord]:
        ...

    def set_proxy_worked_out(self, proxy: ProxyRecord):
        ...

    def get_creds_records(self) -> List[CredsRecord]:
        ...

    def set_creds_worked_out(self, proxy: CredsRecord):
        ...
