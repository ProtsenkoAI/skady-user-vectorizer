from typing import NamedTuple
from interfaces import Proxy, Credentials

# record_fields = [("id", int), ("status_ok", bool), ("status_worked_out", bool), ("time_since_status_change", int)]
#
# ProxyRecord = NamedTuple("ProxyRecord", [*record_fields, ("proxy", Proxy)])
# CredsRecord = NamedTuple("CredsRecord", [*record_fields, ("creds", Credentials)])


class Record:
    def __init__(self, obj_id: int, status_ok: bool, status_worked_out: bool, time_since_status_change: int):
        self.obj_id = obj_id
        self.status_ok = status_ok
        self.status_worked_out = status_worked_out
        self.time_since_status_change = time_since_status_change


class ProxyRecord(Record):
    def __init__(self, *args, proxy: Proxy, **kwargs):
        self.proxy = proxy
        super().__init__(*args, **kwargs)


class CredsRecord(Record):
    def __init__(self, *args, creds: Credentials, **kwargs):
        self.creds = creds
        super().__init__(*args, **kwargs)
