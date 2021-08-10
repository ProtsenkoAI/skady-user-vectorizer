from abc import ABC, abstractmethod


class SessionManager(ABC):
    @abstractmethod
    def next(self):
        ...

    @abstractmethod
    def access_error(self, session_data):
        ...

    @abstractmethod
    def bad_password(self, session_data):
        ...

    @abstractmethod
    def captcha(self, session_data):
        ...
