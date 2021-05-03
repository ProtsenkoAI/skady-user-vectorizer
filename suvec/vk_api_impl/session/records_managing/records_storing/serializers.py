from abc import ABC, abstractmethod
import time
from typing import Dict

from ..session_types import Proxy, Credentials
from ..records import Record, CredsRecord, ProxyRecord
from .db_types import AuthResourceDict, CredsDict, ProxyDict, UserProxyDict, UserCredsDict
from ..consts import RESOURCE_OK_STATUS, RESOURCE_WORKED_OUT_STATUS, CREDS_BAD_PASSWORD_STATUS, ResourceStatus


class AuthRecordsSerializer(ABC):
    RecordStatuses = Dict[str, bool]

    def __init__(self):
        self.next_obj_id = 0

    def to_record(self, raw_dict: AuthResourceDict) -> Record:
        time_since_last_change = time.time() - raw_dict["status_change_time"]
        kwargs_to_create_record = {"time_since_status_change": time_since_last_change,
                                   "obj_id": self.next_obj_id, "status": raw_dict["status"]}
        self.next_obj_id += 1

        return self.create_record(raw_dict, **kwargs_to_create_record)

    @abstractmethod
    def create_record(self, raw_dict: AuthResourceDict, *args, **kwargs):
        ...

    def from_record(self, record: Record) -> AuthResourceDict:
        status_change_time = int(time.time() - record.time_since_status_change)
        kwargs_to_create_res_dict = dict(status=record.status,
                                         status_change_time=status_change_time,)

        return self.create_res_dict(record, **kwargs_to_create_res_dict)

    @abstractmethod
    def create_res_dict(self, record: Record, *args, **kwargs) -> AuthResourceDict:
        ...


class CredsRecordsSerializer(AuthRecordsSerializer):
    RecordStatuses = Dict[str, bool]

    def create_record(self, raw_dict: CredsDict, *args, **kwargs) -> CredsRecord:
        creds = Credentials(email=raw_dict["creds"]["email"], password=raw_dict["creds"]["password"])
        return CredsRecord(*args, creds=creds, **kwargs)

    def create_res_dict(self, record: CredsRecord, *args, **kwargs) -> CredsDict:
        creds = UserCredsDict(email=record.creds.email, password=record.creds.password)
        record_dct = CredsDict(*args, creds=creds, **kwargs)
        return record_dct


class ProxyRecordsSerializer(AuthRecordsSerializer):
    def create_record(self, raw_dict: ProxyDict, *args, **kwargs) -> ProxyRecord:
        proxy = Proxy(address=raw_dict["proxy"]["address"], protocols=raw_dict["proxy"]["protocols"])
        return ProxyRecord(*args, proxy=proxy, **kwargs)

    def create_res_dict(self, record: ProxyRecord, *args, **kwargs) -> ProxyDict:
        proxy = UserProxyDict(address=record.proxy.address, protocols=record.proxy.protocols)
        record_dct = ProxyDict(*args, proxy=proxy, **kwargs)
        return record_dct
