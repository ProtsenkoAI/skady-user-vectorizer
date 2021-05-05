import time
from typing import Optional

from .session_types import Proxy, Credentials
from .consts import ResourceStatus, RESOURCE_OK_STATUS


class Record:
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


class ProxyRecord(Record):
    def __init__(self, *args, proxy: Proxy, **kwargs):
        self.proxy = proxy
        super().__init__(*args, **kwargs)


class CredsRecord(Record):
    def __init__(self, *args, creds: Credentials, **kwargs):
        self.creds = creds
        super().__init__(*args, **kwargs)
