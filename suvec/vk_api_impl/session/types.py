from typing import NamedTuple

from .records_managing.records import ProxyRecord, CredsRecord

SessionData = NamedTuple("SessionData", [("creds", CredsRecord), ("proxy", ProxyRecord)])
