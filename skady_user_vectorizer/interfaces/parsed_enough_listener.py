from abc import ABC, abstractmethod


class ParsedEnoughListener(ABC):
    @abstractmethod
    def parsed_enough(self):
        ...
