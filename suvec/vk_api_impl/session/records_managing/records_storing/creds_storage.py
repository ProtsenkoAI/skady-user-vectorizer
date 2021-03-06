import time

from .storage import AuthRecordsStorage
from ..records import CredsRecord
from ..session_types import Credentials
from ..consts import CREDS_BAD_PASSWORD_STATUS
from .serializers import CredsRecordsSerializer


class CredsStorage(AuthRecordsStorage):
    def __init__(self, save_pth: str):
        super().__init__(save_pth, CredsRecordsSerializer())

    def prepare_record(self, record):
        return record.creds

    def set_bad_password(self, record):
        record.status = CREDS_BAD_PASSWORD_STATUS
        self.dump_records()

    def replace_creds(self, record: CredsRecord, new_email, new_password):
        new_creds = Credentials(new_email, new_password)
        record.creds = new_creds
        self.dump_records()
