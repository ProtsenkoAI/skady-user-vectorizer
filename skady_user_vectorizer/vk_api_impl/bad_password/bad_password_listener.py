from abc import ABC, abstractmethod


class BadPasswordListener(ABC):
    @abstractmethod
    def bad_password(self):
        ...
