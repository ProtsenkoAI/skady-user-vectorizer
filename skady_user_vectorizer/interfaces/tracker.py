from abc import ABC, abstractmethod


class Tracker(ABC):
    # TODO: irrelevant component, please check tracker in vk component and refactor/delete this one
    def __init__(self, print_every: int):
        self.print_every = print_every

    @abstractmethod
    def friends_added(self, friends_nb):
        ...

    @abstractmethod
    def groups_added(self, groups_nb):
        ...
