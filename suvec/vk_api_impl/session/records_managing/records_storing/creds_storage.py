from .storage import AuthRecordsStorage
from ..records import CredsRecord
from ..session_types import Credentials
from ..consts import CREDS_BAD_PASSWORD_STATUS


class CredsStorage(AuthRecordsStorage):
    def set_bad_password(self, bad_password_creds: CredsRecord):
        record = self.get_record_by_id(bad_password_creds.obj_id)
        record.status = CREDS_BAD_PASSWORD_STATUS
        self._dump_records()

    def replace_creds(self, record: CredsRecord, new_email, new_password):
        new_creds = Credentials(new_email, new_password)
        record_in_storage = self.get_record_by_id(record.obj_id)
        record_in_storage.creds = new_creds
