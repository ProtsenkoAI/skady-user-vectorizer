from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, **kwargs):
        super().__init__(storage, *args, **kwargs)

    def mark_bad_password(self, creds_id):
        self.storage: CredsStorage
        self.storage.set_bad_password(creds_id)
