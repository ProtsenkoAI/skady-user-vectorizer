from typing import Optional, Any
from abc import ABC, abstractmethod
import time

from .records import Record
from ..resource_testing import ResourceTester
from .records_storing import AuthRecordsStorage
from .out_of_records_handler import OutOfRecordsHandler
from suvec.common.events_tracking import TerminalEventsTracker
from .consts import RESOURCE_OK_STATUS, RESOURCE_WORKED_OUT_STATUS


class AuthRecordManager(ABC):
    def __init__(self, storage: AuthRecordsStorage, events_tracker: TerminalEventsTracker,
                 out_of_records_handler: OutOfRecordsHandler, record_tester: Optional[ResourceTester] = None,
                 hours_for_resource_reload=24):
        self.storage = storage
        self.tracker = events_tracker
        self.hours_for_reload = hours_for_resource_reload
        self.out_of_records_handler = out_of_records_handler
        self.hours_to_try_again = 1
        self.record_tester = record_tester

    def get_working(self):
        for record in self.storage.get_records():
            if self._check_record_is_usable(record):
                self.storage.set_is_used(record)
                yield self.prepare_record(record)

        else:
            obtained_records = self.out_of_records_handler.run(first_record_id=self.storage.get_next_record_id())
            if len(obtained_records):
                for record in obtained_records:
                    self.storage.add_record(record)
                # recursion, so records handler should return empty records if can't obtain them
                yield from self.get_working()
            # else:
            #     raise RuntimeError("Out of records")

    def mark_free(self, record: Record):
        self.storage.set_is_free(record)

    def mark_worked_out(self, record: Record):
        self.storage.set_worked_out(record)

    @abstractmethod
    def prepare_record(self, record) -> Any:
        """prepare Record object before returning to storage user"""
        ...

    @abstractmethod
    def test_with_record_tester(self, record_tester, record):
        ...

    def _check_record_is_usable(self, record: Record):
        seconds_in_hour = 60 ** 2
        ok_status = record.status == RESOURCE_OK_STATUS
        reloaded = (record.status == RESOURCE_WORKED_OUT_STATUS and
                    record.time_since_status_change / seconds_in_hour >= self.hours_for_reload)
        test_res = False
        if reloaded:
            record.status = RESOURCE_OK_STATUS
        if record.status == RESOURCE_WORKED_OUT_STATUS:
            time_to_check_working = record.time_since_status_change >= seconds_in_hour * self.hours_to_try_again
            if self.record_tester is not None and time_to_check_working:
                test_res = self.test_with_record_tester(self.record_tester, record)
        if test_res:
            record.status = RESOURCE_OK_STATUS

        return ok_status or reloaded or test_res
