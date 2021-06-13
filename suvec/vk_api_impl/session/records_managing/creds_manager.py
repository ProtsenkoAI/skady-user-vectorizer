from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage
from .records import CredsRecord


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, **kwargs):
        super().__init__(storage, *args, **kwargs)

    def prepare_record(self, record: CredsRecord):
        return record.creds.email, record.creds.password

    def mark_bad_password(self, creds_id):
        self.storage: CredsStorage
        self.storage.set_bad_password(creds_id)

    def send_tracker_reset_message(self, resources_total_cnt: int, usable_resources_left_cnt: int):
        self.tracker.creds_report(resources_total_cnt, usable_resources_left_cnt, changed=True)
