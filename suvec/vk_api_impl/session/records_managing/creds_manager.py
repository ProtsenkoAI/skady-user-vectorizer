from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage
from .records import CredsRecord
from .terminal_out_of_records import TerminalOutOfCreds


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, **kwargs):
        super().__init__(storage, *args, out_of_records_handler=TerminalOutOfCreds(), **kwargs)

    def mark_bad_password(self, creds_id):
        self.storage: CredsStorage
        self.storage.set_bad_password(creds_id)

    def test_with_record_tester(self, record_tester, creds):
        return record_tester.test_creds(creds)
