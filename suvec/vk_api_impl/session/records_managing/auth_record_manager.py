from typing import Optional, Callable
from abc import ABC, abstractmethod
import time

from .records import Record
from .records_storing import AuthRecordsStorage
from .out_of_records_handler import OutOfRecordsHandler
from suvec.common.events_tracking import TerminalEventsTracker
from .consts import RESOURCE_OK_STATUS, RESOURCE_WORKED_OUT_STATUS


class AuthRecordManager(ABC):
    def __init__(self, storage: AuthRecordsStorage, events_tracker: TerminalEventsTracker,
                 out_of_records_handler: OutOfRecordsHandler, hours_for_resource_reload=24):
        self.storage = storage
        self.tracker = events_tracker
        self.hours_for_reload = hours_for_resource_reload
        self.out_of_records_handler = out_of_records_handler
        self.min_hours_to_try_resource_again = 1

    def resources(self, record_tester: Optional[Callable] = None):
        """
        :param record_tester: takes prepared record and id to input and returns bool whether record can be used
        """
        # TODO: at the moment calling resources() to often, and every time check all records from start
        #   so need to optimize somehow
        for record, rec_id in self.storage.get_records():
            prepared_record = self.prepare_record(record)

            # TODO: refactor
            seconds_in_hour = 60 ** 2

            if self._check_record_is_usable(record):
                yield prepared_record, rec_id

            elif record_tester is not None and record.time_since_status_change >= seconds_in_hour * self.min_hours_to_try_resource_again:
                record.status_change_time = time.time()
                if record_tester((prepared_record, rec_id)):
                    yield prepared_record, rec_id
        else:
            obtained_records = self.out_of_records_handler.run(first_record_id=self.storage.get_next_record_id())
            if len(obtained_records):
                for record in obtained_records:
                    self.storage.add_record(record)
                # recursion, so records handler should return empty records if can't obtain them
                yield from self.resources(record_tester)
            else:
                raise RuntimeError("Out of records")

    @abstractmethod
    def prepare_record(self, record):
        ...

    @abstractmethod
    def send_tracker_reset_message(self, resources_total_cnt: int, usable_resources_left_cnt: int):
        ...

    def _check_record_is_usable(self, record: Record):
        seconds_in_hour = 60 ** 2
        print("check record is usable", "time since change:", record.time_since_status_change)
        ok_status = record.status == RESOURCE_OK_STATUS
        reloaded = (record.status == RESOURCE_WORKED_OUT_STATUS and
                    record.time_since_status_change / seconds_in_hour >= self.hours_for_reload)
        if reloaded:
            record.status = RESOURCE_OK_STATUS
        return ok_status or reloaded

    def reset_requests_limit(self, resource_id):
        self.storage.set_worked_out(resource_id)
        self._prepare_and_send_tracker_reset_message()

    def _prepare_and_send_tracker_reset_message(self):
        resources_left, usable_resources_left = 0, 0
        for record, record_id in self.storage.get_records():
            resources_left += 1
            if self._check_record_is_usable(record):
                usable_resources_left += 1
        self.send_tracker_reset_message(resources_left, usable_resources_left)
