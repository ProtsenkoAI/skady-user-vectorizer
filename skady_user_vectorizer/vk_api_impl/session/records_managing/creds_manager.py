from .auth_record_manager import AuthRecordManager
from .records_storing.creds_storage import CredsStorage
from .records import CredsRecord


class CredsManager(AuthRecordManager):
    def __init__(self, storage: CredsStorage, *args, **kwargs):
        super().__init__(storage, *args, **kwargs)

    def get(self):
        """Process contained resource as subclass wants and return it to user class (probably session manager)"""
        self.resource: CredsRecord
        return self.resource.creds

    def reset_bad_password(self):
        if self.resource is not None:
            self.storage.set_bad_password(self.resource)
        self.reset_resource()

    def send_tracker_reset_message(self, resources_total_cnt: int, usable_resources_left_cnt: int):
        self.tracker.creds_report(resources_total_cnt, usable_resources_left_cnt, changed=True)
