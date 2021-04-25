from interfaces import Credentials
from .creds_storage_interface import CredsStorage
from .records import CredsRecord


class CredsManager:
    # TODO: add typings
    # TODO: add reasons why reset proxy/password (bad password, unknown, worked_etc)
    def __init__(self, creds_storage: CredsStorage):
        self.storage = creds_storage

        self.creds_record = self._get_new_creds_record()

    def _get_new_creds_record(self) -> CredsRecord:
        for creds_record in self.storage.get_creds_records():
            if self._check_usable_creds(creds_record):
                return creds_record

    def _check_usable_creds(self, creds_record: CredsRecord):
        return (creds_record.status_ok or
                creds_record.status_worked_out and creds_record.time_passed >= CREDS_RELOAD_TIME)

    def get(self) -> Credentials:
        return self.creds_record.creds

    def reset(self):
        self.storage.set_creds_worked_out(self.creds_record)
        self.creds_record = self._get_new_creds_record()
