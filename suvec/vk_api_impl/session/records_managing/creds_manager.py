from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage
from .records import CredsRecord


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, **kwargs):
        super().__init__(storage, *args, **kwargs)

    def prepare_record(self, record: CredsRecord):
        return record.creds

    def mark_bad_password(self, creds_id):
        self.storage: CredsStorage
        self.storage.set_bad_password(creds_id)

    def test_with_record_tester(self, record_tester, creds):
        return record_tester.test_creds(creds)
