from typing import List

from ..records import Record
from .records_file import RecordsFile
from .serializers import AuthRecordsSerializer
from ..consts import RESOURCE_WORKED_OUT_STATUS, RESOURCE_ALREADY_USED, RESOURCE_OK_STATUS


class AuthRecordsStorage:
    def __init__(self, save_pth: str, records_serializer: AuthRecordsSerializer):
        self.save_pth = save_pth
        self.records_file = RecordsFile(save_pth, records_serializer)
        self.records = self.records_file.read_records()
        self._last_record_id = -1

    def get_records(self) -> List[Record]:
        return self.records

    def set_worked_out(self, record: Record):
        record.status = RESOURCE_WORKED_OUT_STATUS
        self.dump_records()

    def set_is_used(self, record: Record):
        record.status = RESOURCE_ALREADY_USED
        self.dump_records()

    def set_is_free(self, record: Record):
        record.status = RESOURCE_OK_STATUS
        self.dump_records()

    def get_record_idx_by_id(self, rec_id: int) -> int:
        for idx, (record, record_id) in enumerate(self.records):
            if record_id == rec_id:
                return idx

    def add_record(self, record: Record, allow_duplicates=False):
        if allow_duplicates or not record.is_in(self.records):
            self.records.append(record)
            self.dump_records()

    def dump_records(self):
        self.records_file.write(self.records)

    def get_next_record_id(self):
        self._last_record_id += 1
        return self._last_record_id
