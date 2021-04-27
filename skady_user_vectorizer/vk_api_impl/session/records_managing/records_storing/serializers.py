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
        statuses = self.get_statuses_from_raw(raw_dict)

        time_since_last_change = time.time() - raw_dict["status_change_time"]
        kwargs_to_create_record = {"time_since_status_change": time_since_last_change,
                                   "obj_id": self.next_obj_id, **statuses}
        self.next_obj_id += 1

        return self.create_record(raw_dict, **kwargs_to_create_record)

    def get_statuses_from_raw(self, raw_dict: AuthResourceDict) -> RecordStatuses:
        if raw_dict["status"] == RESOURCE_OK_STATUS:
            status_ok = True
            status_worked_out = False
        else:
            status_ok = False
            if raw_dict["status"] == RESOURCE_WORKED_OUT_STATUS:
                status_worked_out = True
            else:
                status_worked_out = False
        return {"status_worked_out": status_worked_out, "status_ok": status_ok}

    @abstractmethod
    def create_record(self, raw_dict: AuthResourceDict, *args, **kwargs):
        ...

    def from_record(self, record: Record) -> AuthResourceDict:
        status_change_time = int(time.time() - record.time_since_status_change)
        status = self.get_record_status(record)

        kwargs_to_create_res_dict = dict(status=status,
                                         status_change_time=status_change_time,)

        return self.create_res_dict(record, **kwargs_to_create_res_dict)

    def get_record_status(self, record: Record) -> ResourceStatus:
        if record.status_ok:
            return RESOURCE_OK_STATUS
        elif record.status_worked_out:
            return RESOURCE_WORKED_OUT_STATUS
        else:
            raise ValueError(f"Unknown status of record. record: {record}")

    @abstractmethod
    def create_res_dict(self, record: Record, *args, **kwargs) -> AuthResourceDict:
        ...


class CredsRecordsSerializer(AuthRecordsSerializer):
    RecordStatuses = Dict[str, bool]

    def create_record(self, raw_dict: CredsDict, *args, **kwargs) -> CredsRecord:
        creds = Credentials(email=raw_dict["creds"]["email"], password=raw_dict["creds"]["password"])
        return CredsRecord(*args, creds=creds, **kwargs)

    def get_record_status(self, record: CredsRecord) -> ResourceStatus:
        if record.status_bad_password:
            return CREDS_BAD_PASSWORD_STATUS
        else:
            return super().get_record_status(record)

    def get_statuses_from_raw(self, raw_dict: CredsDict) -> RecordStatuses:
        status_bad_password = raw_dict["status"] == CREDS_BAD_PASSWORD_STATUS
        statuses = super().get_statuses_from_raw(raw_dict)
        statuses["status_bad_password"] = status_bad_password
        return statuses

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
