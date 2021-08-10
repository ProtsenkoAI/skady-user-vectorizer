from typing import Optional
from abc import ABC

from .records import Record
from .records_storing import AuthRecordsStorage
from .out_of_records_handler import OutOfRecordsHandler
from suvec.common.events_tracking import TerminalEventsTracker
from .consts import RESOURCE_OK_STATUS


class AuthRecordManager(ABC):
    # TODO: replace out_of_records handler with just exiting till the next day
    def __init__(self, storage: AuthRecordsStorage, events_tracker: TerminalEventsTracker,
                 out_of_records_handler: Optional[OutOfRecordsHandler],
                 hours_for_resource_reload=24):
        self.storage = storage
        self.tracker = events_tracker
        self.hours_for_reload = hours_for_resource_reload
        self.out_of_records_handler = out_of_records_handler

    def get_working(self):
        nb_good_found = 0
        for record in self.storage.get_records():
            if self._check_record_is_usable(record):
                print("yielding record", record)
                self.storage.set_is_used(record)
                nb_good_found += 1
                yield record
        else:
            if self.out_of_records_handler is not None:
                obtained_records = self.out_of_records_handler.run(first_record_id=self.storage.get_next_record_id())
                if len(obtained_records):
                    for record in obtained_records:
                        nb_good_found += 1
                        self.storage.add_record(record)
        # recursion, so records handler should return empty records if can't obtain them
        if nb_good_found > 0:  # if hadn't found any resources it's useless to call recursion again, we just needed loop
            yield from self.get_working()

    def mark_free(self, record: Record):
        print(f"mark record {record.obj_id} as free")
        self.storage.set_is_free(record)

    def mark_worked_out(self, record: Record):
        print(f"mark record {record.obj_id} as worked out")
        self.storage.set_worked_out(record)

    def _check_record_is_usable(self, record: Record):
        seconds_in_hour = 60 ** 2
        reloaded = record.time_since_status_change / seconds_in_hour >= self.hours_for_reload
        ok_status = record.status == RESOURCE_OK_STATUS or reloaded
        return ok_status
