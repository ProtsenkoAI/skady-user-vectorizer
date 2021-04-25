from abc import ABC, abstractmethod
from typing import List

from .records import CredsRecord


class CredsStorage(ABC):
    @abstractmethod
    def get_creds_records(self) -> List[CredsRecord]:
        ...

    @abstractmethod
    def set_creds_worked_out(self, proxy: CredsRecord):
        ...
