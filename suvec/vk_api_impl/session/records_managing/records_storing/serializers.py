from abc import ABC, abstractmethod
from typing import Dict

from ..session_types import Proxy, Credentials
from ..records import Record, CredsRecord, ProxyRecord
from ..consts import RESOURCE_ALREADY_USED, RESOURCE_OK_STATUS
from .db_types import AuthResourceDict, CredsDict, ProxyDict, UserProxyDict, UserCredsDict


class AuthRecordsSerializer(ABC):
    RecordStatuses = Dict[str, bool]

    def __init__(self):
        self.next_obj_id = 0

    def to_record(self, raw_dict: AuthResourceDict) -> Record:
        kwargs_to_create_record = {"status_change_time": raw_dict['status_change_time'],
                                   "obj_id": self.next_obj_id, "status": raw_dict["status"]}
        self.next_obj_id += 1

        return self.create_record(raw_dict, **kwargs_to_create_record)

    @abstractmethod
    def create_record(self, raw_dict: AuthResourceDict, *args, **kwargs):
        ...

    def from_record(self, record: Record) -> AuthResourceDict:
        # don't dump that record is used in this session, just mark this session is ok
        if record.status != RESOURCE_ALREADY_USED:
            status = record.status
        else:
            status = RESOURCE_OK_STATUS
        kwargs_to_create_res_dict = dict(status=status,
                                         status_change_time=record.status_change_time)

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
        proxy = Proxy(address=raw_dict["proxy"]["address"])
        return ProxyRecord(*args, proxy=proxy, **kwargs)

    def create_res_dict(self, record: ProxyRecord, *args, **kwargs) -> ProxyDict:
        proxy = UserProxyDict(address=record.proxy.address)
        record_dct = ProxyDict(*args, proxy=proxy, **kwargs)
        return record_dct
