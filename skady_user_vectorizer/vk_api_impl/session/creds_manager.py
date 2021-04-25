from interfaces import Credentials
from .creds_storage_interface import CredsStorage
from .records import CredsRecord
from .consts import CREDS_RELOAD_TIME
from ..events_tracker import EventsTracker


class CredsManager:
    # TODO: add reasons why reset creds (bad password, unknown, worked out)
    def __init__(self, creds_storage: CredsStorage, events_tracker: EventsTracker):
        self.storage = creds_storage
        self.tracker = events_tracker

        self.creds_record = None

    def _get_new_creds_record(self) -> CredsRecord:
        for creds_record in self.storage.get_creds_records():
            if self._check_usable_creds(creds_record):
                return creds_record
        else:
            raise RuntimeError("Out of creds")

    def _check_usable_creds(self, creds_record: CredsRecord):
        return (creds_record.status_ok or
                creds_record.status_worked_out and creds_record.time_since_status_change >= CREDS_RELOAD_TIME)

    def get(self) -> Credentials:
        return self.creds_record.creds

    def reset(self):
        creds_left, usable_creds_left = 0, 0
        for record in self.storage.get_creds_records():
            creds_left += 1
            if self._check_usable_creds(record):
                usable_creds_left += 1

        self.tracker.creds_report(creds_left, usable_creds_left, changed=True)
        if self.creds_record is not None:
            self.storage.set_creds_worked_out(self.creds_record)
        self.creds_record = self._get_new_creds_record()
