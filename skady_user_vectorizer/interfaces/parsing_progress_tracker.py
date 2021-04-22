from abc import ABC, abstractmethod


class ParsingProgressTracker(ABC):
    @abstractmethod
    def friends_added(self, friends_nb):
        ...

    @abstractmethod
    def groups_added(self, groups_nb):
        ...
