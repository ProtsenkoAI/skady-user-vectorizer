from abc import ABC, abstractmethod
from typing import List
from .records import ProxyRecord


class ProxyStorage(ABC):
    @abstractmethod
    def get_proxy_records(self) -> List[ProxyRecord]:
        ...

    @abstractmethod
    def set_proxy_worked_out(self, proxy: ProxyRecord):
        ...
