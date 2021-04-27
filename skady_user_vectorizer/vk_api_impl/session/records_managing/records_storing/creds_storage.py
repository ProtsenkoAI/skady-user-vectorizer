from .storage import AuthRecordsStorage
from ..records import CredsRecord


class CredsStorage(AuthRecordsStorage):
    def set_bad_password(self, bad_password_creds: CredsRecord):
        record = self.get_record_by_id(bad_password_creds.obj_id)
        record.status_ok = False
        record.status_bad_password = True
        self._dump_records()
