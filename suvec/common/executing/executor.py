from abc import ABC, abstractmethod
from typing import List

from suvec.common.requesting import Request
from suvec.common.executing import ParseRes


class Executor(ABC):
    @abstractmethod
    def execute(self, requests: List[Request]) -> List[ParseRes]:
        ...
