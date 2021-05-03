from typing import List
import json

from ..records import Record
from .serializers import AuthRecordsSerializer
from ..consts import RESOURCE_WORKED_OUT_STATUS


class AuthRecordsStorage:
    # TODO: every time asked to get_records, need to load them from file
    # TODO: maybe replace private _dump_records() with write() and call it from users objects
    def __init__(self, save_pth: str, records_serializer: AuthRecordsSerializer):
        self.save_pth = save_pth
        self.serializer = records_serializer
        with open(save_pth) as f:
            records = json.load(f)

        self.records = self._parse_loaded_records(records)

    def _parse_loaded_records(self, raw_records: List[dict]) -> List[Record]:
        return [self.serializer.to_record(raw_rec) for raw_rec in raw_records]

    def get_records(self) -> List[Record]:
        return self.records

    def set_worked_out(self, worked_out_record: Record):
        # TODO: move set_worked_out to manager, keep there only read/write operations
        record = self.get_record_by_id(worked_out_record.obj_id)
        record.status = RESOURCE_WORKED_OUT_STATUS
        self._dump_records()

    def get_record_by_id(self, record_id) -> Record:
        rec_idx = self.get_record_idx_by_id(record_id)
        return self.records[rec_idx]

    def delete_record(self, record: Record):
        record_idx = self.get_record_idx_by_id(record.obj_id)
        if record_idx is not None:
            self.records.pop(record_idx)
        self._dump_records()

    def get_record_idx_by_id(self, obj_id: int) -> int:
        for idx, record in enumerate(self.records):
            if record.obj_id == obj_id:
                return idx

    def add_record(self, record: Record):
        self.records.append(record)
        self._dump_records()

    def _dump_records(self):
        serialized = [self.serializer.from_record(rec) for rec in self.records]
        with open(self.save_pth, "w") as f:
            json.dump(serialized, f)