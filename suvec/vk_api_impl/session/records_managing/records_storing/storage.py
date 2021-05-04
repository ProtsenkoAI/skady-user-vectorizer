from typing import List
import json
import os

from ..records import Record
from .db_types import AuthResourceDict
from .serializers import AuthRecordsSerializer
from ..consts import RESOURCE_WORKED_OUT_STATUS


class AuthRecordsStorage:
    # TODO: maybe split to 2 objects: one will read, serialize, write. Second will delete, add, filter, get by idx etc.
    def __init__(self, save_pth: str, records_serializer: AuthRecordsSerializer):
        self.save_pth = save_pth
        self.serializer = records_serializer
        records = self._read_records(save_pth)
        self.records = self._parse_loaded_records(records)

    def _read_records(self, save_pth: str) -> List[AuthResourceDict]:
        if os.path.isfile(save_pth):
            with open(save_pth) as f:
                return json.load(f)
        else:
            with open(save_pth, "w") as f:
                json.dump([], f)
                return []

    def _parse_loaded_records(self, raw_records: List[dict]) -> List[Record]:
        return [self.serializer.to_record(raw_rec) for raw_rec in raw_records]

    def get_records(self) -> List[Record]:
        return self.records

    def set_worked_out(self, worked_out_record: Record):
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

    def get_next_record_id(self) -> int:
        max_id = 0
        for record in self.records:
            max_id = max(max_id, record.obj_id)
        return max_id + 1

    def _dump_records(self):
        serialized = [self.serializer.from_record(rec) for rec in self.records]
        with open(self.save_pth, "w") as f:
            json.dump(serialized, f)
