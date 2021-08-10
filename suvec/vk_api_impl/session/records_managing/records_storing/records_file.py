from typing import List
import os
import json

from .serializers import AuthRecordsSerializer
from ..records import Record


class RecordsFile:
    def __init__(self, pth: str, serializer: AuthRecordsSerializer):
        self.pth = pth
        self.serializer = serializer

    def read_records(self) -> List[Record]:
        if os.path.isfile(self.pth):
            with open(self.pth) as f:
                raw_recs = json.load(f)
        else:
            with open(self.pth, "w") as f:
                json.dump([], f)
                raw_recs = []
        return self._parse_loaded_records(raw_recs)

    def write(self, records: List[Record]):
        serialized = [self.serializer.from_record(rec) for rec in records]
        with open(self.pth, "w") as f:
            json.dump(serialized, f)

    def _parse_loaded_records(self, raw_records: List[dict]):
        records = [self.serializer.to_record(raw_rec) for raw_rec in raw_records]
        return records
