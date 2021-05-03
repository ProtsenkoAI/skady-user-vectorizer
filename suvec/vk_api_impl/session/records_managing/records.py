from .session_types import Proxy, Credentials
from .consts import ResourceStatus


class Record:
    # TODO: maybe we will need a validation that for some class are set only allowed statuses
    def __init__(self, obj_id: int, status: ResourceStatus, time_since_status_change: int):
        self.obj_id = obj_id
        self.status = status
        self.time_since_status_change = time_since_status_change


class ProxyRecord(Record):
    def __init__(self, *args, proxy: Proxy, **kwargs):
        self.proxy = proxy
        super().__init__(*args, **kwargs)


class CredsRecord(Record):
    def __init__(self, *args, creds: Credentials, **kwargs):
        self.creds = creds
        super().__init__(*args, **kwargs)