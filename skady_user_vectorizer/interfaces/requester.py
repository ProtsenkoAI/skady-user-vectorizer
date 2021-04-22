from abc import ABC, abstractmethod


class Requester(ABC):
    """Have to somehow expand number of users parsed, it's the class own duty"""
    @abstractmethod
    def add_users(self, users):
        ...

    @abstractmethod
    def get_requests(self):
        ...
