import time
from typing import Optional, List
from abc import abstractmethod, ABC

from .session_types import Proxy, Credentials
from .consts import ResourceStatus, RESOURCE_OK_STATUS


class Record(ABC):
    def __init__(self, obj_id: int, status: ResourceStatus = RESOURCE_OK_STATUS,
                 status_change_time: Optional[int] = None):
        if status_change_time is None:
            status_change_time = time.time()
        self.obj_id = obj_id
        self.status = status
        self.status_change_time = status_change_time

    @property
    def time_since_status_change(self):
        return time.time() - self.status_change_time

    def is_in(self, records: List):
        for record in records:
            if self.check_same(record):
                return True

        return False

    @abstractmethod
    def check_same(self, record):
        """Check that both records represent same resource (for example, same proxy address)"""
        ...


class ProxyRecord(Record):
    def __init__(self, *args, proxy: Proxy, **kwargs):
        self.proxy = proxy
        super().__init__(*args, **kwargs)

    def check_same(self, record):
        return self.proxy == record.proxy


class CredsRecord(Record):
    def __init__(self, *args, creds: Credentials, **kwargs):
        self.creds = creds
        super().__init__(*args, **kwargs)

    def check_same(self, record):
        return self.creds == record.creds
