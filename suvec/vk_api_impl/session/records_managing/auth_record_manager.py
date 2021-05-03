from abc import ABC, abstractmethod

from .records import Record
from .records_storing import AuthRecordsStorage
from suvec.common.events_tracking import TerminalEventsTracker
from .consts import RESOURCE_OK_STATUS, RESOURCE_WORKED_OUT_STATUS


class AuthRecordManager(ABC):
    def __init__(self, storage: AuthRecordsStorage, events_tracker: TerminalEventsTracker,
                 hours_for_resource_reload=24):
        self.storage = storage
        self.tracker = events_tracker
        self.hours_for_reload = hours_for_resource_reload

        self.resource = self._get_new_record()

    @abstractmethod
    def get(self):
        """Process contained resource as subclass wants and return it to user class (probably session manager)"""
        ...

    @abstractmethod
    def send_tracker_reset_message(self, resources_total_cnt: int, usable_resources_left_cnt: int):
        ...

    def _get_new_record(self) -> Record:
        for record in self.storage.get_records():
            if self._check_record_is_usable(record):
                return record
        else:
            raise RuntimeError("Out of records")

    def _check_record_is_usable(self, record: Record):
        seconds_in_hour = 60 ** 2
        return (record.status == RESOURCE_OK_STATUS or
                record.status == RESOURCE_WORKED_OUT_STATUS and
                record.time_since_status_change / seconds_in_hour >= self.hours_for_reload)

    def reset_requests_limit(self):
        if self.resource is not None:
            self.storage.set_worked_out(self.resource)
        self.reset_resource()

    def reset_resource(self):
        self.resource = self._get_new_record()
        self._prepare_and_send_tracker_reset_message()

    def _prepare_and_send_tracker_reset_message(self):
        resources_left, usable_resources_left = 0, 0
        for record in self.storage.get_records():
            resources_left += 1
            if self._check_record_is_usable(record):
                usable_resources_left += 1
        self.send_tracker_reset_message(resources_left, usable_resources_left)
