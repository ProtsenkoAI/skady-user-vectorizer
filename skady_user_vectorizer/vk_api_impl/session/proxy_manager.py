from interfaces import Proxy
from .proxy_storage_interface import ProxyStorage
from .records import ProxyRecord
from .consts import PROXY_RELOAD_TIME


class ProxyManager:
    def __init__(self, proxy_storage: ProxyStorage, events_tracker):
        self.tracker = events_tracker
        self.storage = proxy_storage
        self.proxy_record = self._get_new_proxy_record()

    def _get_new_proxy_record(self) -> ProxyRecord:
        for proxy_record in self.storage.get_proxy_records():
            if self._check_usable_proxy(proxy_record):
                return proxy_record

    def _check_usable_proxy(self, proxy_record: ProxyRecord) -> bool:
        return (proxy_record.status_ok or
                proxy_record.status_worked_out and proxy_record.time_since_status_change >= PROXY_RELOAD_TIME)

    def get(self) -> Proxy:
        return self.proxy_record.proxy

    def reset(self):
        proxy_left, usable_proxy_left = 0, 0
        for record in self.storage.get_proxy_records():
            proxy_left += 1
            if self._check_usable_proxy(record):
                usable_proxy_left += 1

        self.tracker.proxy_report(proxy_left, usable_proxy_left, changed=True)
        self.storage.set_proxy_worked_out(self.proxy_record)
        self.proxy_record = self._get_new_proxy_record()
