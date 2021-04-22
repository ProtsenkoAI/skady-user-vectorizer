from abc import ABC, abstractmethod


class AccessErrorListener(ABC):
    @abstractmethod
    def access_error_occurred(self):
        ...
