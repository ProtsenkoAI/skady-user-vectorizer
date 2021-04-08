from util import read_config
from .info_retriever import InfoRetriever

from typing import Any, List


User = Any


class UsersCollector:
    # TODO: add progress bar
    def __init__(self):
        self.accumulated_users = []
        self.info_retriever = InfoRetriever(read_config())

    def run(self, start_user: User, nb_processed_friends: int = 10, need_to_obtain: int = 1000):
        users_whose_friends_get = [start_user]

        while len(self.accumulated_users) < need_to_obtain:
            new_users = self.info_retriever.get_friends(users_whose_friends_get)
            new_users_filtered = self._filter_friends(new_users, nb_processed_friends)
            self.accumulated_users.extend(new_users_filtered)

            users_whose_friends_get = new_users_filtered

    def _filter_friends(self, obtained_friends: List[User], max_nb: int) -> List[User]:
        filtered_by_num = obtained_friends[:max_nb]
        are_groups_open_mask = self.info_retriever.check_groups_open(filtered_by_num)
        only_with_open_groups = [user for is_open, user in zip(are_groups_open_mask, filtered_by_num) if is_open]
        return only_with_open_groups
