from abc import ABC, abstractmethod
from typing import List

from ..executing import ParseRes
from ..top_level_types import User


class ParsedProcessor(ABC):
    @abstractmethod
    def process(self, parsed_results: ParseRes, *args, **kwargs):
        ...

    @abstractmethod
    def process_success(self, res: ParseRes):
        ...

    @abstractmethod
    def get_new_parse_candidates(self) -> List[User]:
        ...
