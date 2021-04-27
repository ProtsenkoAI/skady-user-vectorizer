from typing import List
import json

from ..records import Record
from .serializers import AuthRecordsSerializer


class AuthRecordsStorage:
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
        for record in self.records:
            if record.obj_id == worked_out_record.obj_id:
                record.status_ok = False
                record.status_worked_out = True
                self._dump_records()
                break

    def _dump_records(self):
        serialized = [self.serializer.from_record(rec) for rec in self.records]
        with open(self.save_pth, "w") as f:
            json.dump(serialized, f)