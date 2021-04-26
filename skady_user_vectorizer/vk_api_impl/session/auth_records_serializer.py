from abc import ABC, abstractmethod
import time

from interfaces import Proxy, Credentials
from .records import Record, CredsRecord, ProxyRecord
from .db_types import AuthResourceDict, CredsDict, ProxyDict, UserProxyDict, UserCredsDict
from .consts import RESOURCE_OK_STATUS, RESOURCE_WORKED_OUT_STATUS


class AuthRecordsSerializer(ABC):
    def to_record(self, raw_dict: AuthResourceDict) -> Record:
        if raw_dict["status"] == RESOURCE_OK_STATUS:
            status_ok = True
            status_worked_out = False
        else:
            status_ok = False
            if raw_dict["status"] == RESOURCE_WORKED_OUT_STATUS:
                status_worked_out = True
            else:
                status_worked_out = False

        time_since_last_change = time.time() - raw_dict["status_change_time"]
        kwargs_to_create_record = {"status_ok": status_ok, "status_worked_out": status_worked_out,
                                   "time_since_status_change": time_since_last_change,
                                   "obj_id": raw_dict["obj_id"]}

        return self.create_record(raw_dict, **kwargs_to_create_record)

    @abstractmethod
    def create_record(self, raw_dict: AuthResourceDict, *args, **kwargs):
        ...

    def from_record(self, record: Record) -> AuthResourceDict:
        if record.status_ok:
            status = RESOURCE_OK_STATUS
        elif record.status_worked_out:
            status = RESOURCE_WORKED_OUT_STATUS
        else:
            raise ValueError(f"Unknown status of record. record: {record}")
        status_change_time = int(time.time() - record.time_since_status_change)

        kwargs_to_create_res_dict = dict(status=status,
                                         status_change_time=status_change_time,)

        return self.create_res_dict(record, **kwargs_to_create_res_dict)

    @abstractmethod
    def create_res_dict(self, record: Record, *args, **kwargs) -> AuthResourceDict:
        ...


class CredsRecordsSerializer(AuthRecordsSerializer):
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
