# TODO: add input timeouts

from typing import List
import time
from abc import ABC, abstractmethod

from .records import Record, CredsRecord, ProxyRecord
from .session_types import Credentials, Proxy
from .out_of_records_handler import OutOfRecordsHandler


class TerminalOutOfRecords(OutOfRecordsHandler, ABC):
    def run(self, first_record_id: int) -> List[Record]:
        print("Oops! Have no working proxies left")
        print("Please, enter new credentials, or parsing will be terminated")

        resources = []
        rec_id = first_record_id
        while True:
            terminate = input("Starting enter new creds, if want to terminate, enter 'T', otherwise N\n")
            if terminate == "Y":
                return resources
            resources.append(self.receive_input_and_create_record(rec_id))
            rec_id += 1

    @abstractmethod
    def receive_input_and_create_record(self, obj_id: int) -> Record:
        ...


class TerminalOutOfCreds(TerminalOutOfRecords):

    def receive_input_and_create_record(self, obj_id: int) -> Record:
        email = input("Email:\n")
        password = input("Password:\n")

        return CredsRecord(creds=Credentials(email, password), obj_id=obj_id, status_change_time=time.time())


class TerminalOutOfProxy(TerminalOutOfRecords):
    def receive_input_and_create_record(self, obj_id: int) -> Record:
        address = input("Proxy address:\n")

        return ProxyRecord(proxy=Proxy(address), obj_id=obj_id, status_change_time=time.time())
