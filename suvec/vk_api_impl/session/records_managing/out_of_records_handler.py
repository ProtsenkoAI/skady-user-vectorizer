from abc import ABC, abstractmethod
from typing import List

from .records import Record


class OutOfRecordsHandler(ABC):
    @abstractmethod
    def run(self, first_record_id: int) -> List[Record]:
        ...
