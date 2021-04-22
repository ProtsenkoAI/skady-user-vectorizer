from abc import ABC, abstractmethod
from .processed_user_res import UserGroupsRes, UserFriendsRes


class InfoRetriever(ABC):
    # TODO: apply max friends
    @abstractmethod
    def get_groups(self, groups_response) -> UserGroupsRes:
        ...

    @abstractmethod
    def get_friends(self, friends_response) -> UserFriendsRes:
        ...
