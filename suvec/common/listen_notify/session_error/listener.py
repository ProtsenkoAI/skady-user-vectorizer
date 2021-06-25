from abc import ABC, abstractmethod, ABCMeta


class SessionErrorListener(ABC):
    @abstractmethod
    def session_error_occurred(self, session_id: int):
        ...

    @abstractmethod
    def proxy_error_occurred(self, session_id: int):
        ...

    @abstractmethod
    def bad_password(self, session_id: int):
        ...


class AbstractSessionErrorListener(SessionErrorListener, ABC, metaclass=ABCMeta):
    # Needed for ABC classes inheriting from Listener
    ...
