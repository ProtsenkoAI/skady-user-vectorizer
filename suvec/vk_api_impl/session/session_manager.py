from abc import ABC, abstractmethod
from .sessions_containers import SessionsContainer


class SessionManager(ABC):
    @abstractmethod
    def allocate_sessions(self, n: int, container: SessionsContainer):
        ...
