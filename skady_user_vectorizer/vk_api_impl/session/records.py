from typing import NamedTuple
from interfaces import Proxy, Credentials

record_fields = [("id", int), ("status_ok", bool), ("status_worked_out", bool), ("time_since_status_change", int)]

ProxyRecord = NamedTuple("ProxyRecord", [*record_fields, ("proxy", Proxy)])
CredsRecord = NamedTuple("CredsRecord", [*record_fields, ("creds", Credentials)])
