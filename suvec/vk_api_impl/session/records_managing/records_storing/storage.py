from typing import List, Tuple
import json
import time
import os

from ..records import Record
from .db_types import AuthResourceDict
from .serializers import AuthRecordsSerializer
from ..consts import RESOURCE_WORKED_OUT_STATUS


class AuthRecordsStorage:
    RecordWithId = Tuple[Record, int]
    # TODO: maybe split to 2 objects: one will read, serialize, write. Second will delete, add, filter, get by idx etc.

    def __init__(self, save_pth: str, records_serializer: AuthRecordsSerializer):
        self.save_pth = save_pth
        self.serializer = records_serializer
        records = self._read_records(save_pth)
        self.records = self._parse_loaded_records(records)
        self._last_record_id = -1

    def _read_records(self, save_pth: str) -> List[AuthResourceDict]:
        if os.path.isfile(save_pth):
            with open(save_pth) as f:
                return json.load(f)
        else:
            with open(save_pth, "w") as f:
                json.dump([], f)
                return []

    def _parse_loaded_records(self, raw_records: List[dict]) -> List[RecordWithId]:
        records = [(self.serializer.to_record(raw_rec), idx) for idx, raw_rec in enumerate(raw_records)]
        self._last_record_id = records[-1][-1]
        return records

    def get_records(self) -> List[RecordWithId]:
        return self.records

    def set_worked_out(self, record_id):
        record = self.get_record_by_id(record_id)
        record.status = RESOURCE_WORKED_OUT_STATUS
        record.status_change_time = time.time()
        self.dump_records()

    def get_record_by_id(self, record_id) -> Record:
        rec_idx = self.get_record_idx_by_id(record_id)
        record, record_id = self.records[rec_idx]
        return record

    def delete_record(self, record: Record):
        record_idx = self.get_record_idx_by_id(record.obj_id)
        if record_idx is not None:
            self.records.pop(record_idx)
        self.dump_records()

    def get_record_idx_by_id(self, rec_id: int) -> int:
        for idx, (record, record_id) in enumerate(self.records):
            if record_id == rec_id:
                return idx

    def add_record(self, record: Record, allow_duplicates=False):
        if allow_duplicates or not record.is_in(self.records):
            self.records.append((record, self.get_next_record_id()))
        self.dump_records()

    def dump_records(self):
        serialized = [self.serializer.from_record(rec) for (rec, rec_id) in self.records]
        with open(self.save_pth, "w") as f:
            json.dump(serialized, f)

    def get_next_record_id(self):
        self._last_record_id += 1
        return self._last_record_id
