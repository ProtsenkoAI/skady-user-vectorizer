from abc import ABC, abstractmethod


class SessionLimitListener(ABC):
    @abstractmethod
    def session_limit(self):
        ...
