from abc import ABC, abstractmethod, ABCMeta


class AccessErrorListener(ABC):
    @abstractmethod
    def access_error_occurred(self, parse_res):
        ...


class AbstractAccessErrorListener(AccessErrorListener, ABC, metaclass=ABCMeta):
    # Needed for ABC classes inheriting from Listener
    ...
