from interfaces import Proxy
from .proxy_storage_interface import ProxyStorage
from .records import ProxyRecord


class ProxyManager:
    def __init__(self, proxy_storage: ProxyStorage):
        self.storage = proxy_storage
        self.proxy_record = self._get_new_proxy_record()

    def _get_new_proxy_record(self) -> ProxyRecord:
        for proxy_record in self.storage.get_proxy_records():
            if self._check_usable_proxy(proxy_record):
                return proxy_record

    def _check_usable_proxy(self, proxy_record: ProxyRecord) -> bool:
        return (proxy_record.status_ok or
                proxy_record.status_worked_out and proxy_record.time_passed >= PROXY_RELOAD_TIME)

    def get(self) -> Proxy:
        return self.proxy_record.proxy

    def reset(self):
        self.storage.set_proxy_worked_out(self.proxy_record)
        self.proxy_record = self._get_new_proxy_record()
