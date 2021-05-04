from abc import ABC, abstractmethod, ABCMeta


class AccessErrorListener(ABC):
    @abstractmethod
    def access_error_occurred(self, user, type_of_request: str, *args, **kwargs):
        ...


class AbstractAccessErrorListener(AccessErrorListener, ABC, metaclass=ABCMeta):
    ...
