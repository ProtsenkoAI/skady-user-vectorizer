from abc import ABC, abstractmethod
from .parse_statuses import UserProcStatus


class ParsingLogger(ABC):
    @abstractmethod
    def log_parse_error(self, status: UserProcStatus, desc: str):
        ...

    @abstractmethod
    def log_info(self, msg: str):
        ...
