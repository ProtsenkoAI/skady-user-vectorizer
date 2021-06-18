import unittest
import guppy
import random

from suvec.common.requesting import DuplicateUsersFilter
from suvec.common.top_level_types import User


class TestDuplicateUsersFilter(unittest.TestCase):
    def test_memory_usage(self):
        """Performs a lot of filtering on many users and checks memory usage"""
        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size

        users_filt = DuplicateUsersFilter()
        step = 10 ** 5
        for start_user_id in range(0, 10 ** 6, step):
            users = [User(usr_id) for usr_id in range(start_user_id, start_user_id + step)]
            users_filt(users)
        del users

        memory_used_by_filter = memory_checker.heap().size - memory_usage_before
        bytes_per_user = 72  # a lot of memory because of py objects and hashmap of added users
        self.assertLess(memory_used_by_filter, 10 ** 6 * bytes_per_user)

    def test_unique_users(self):
        """Checks that no user can be returned twice"""
        def _create_users():
            return [User(usr_id) for usr_id in range(10 ** 3)]

        users_filt = DuplicateUsersFilter()

        dupl_users = _create_users()
        dupl_users += _create_users()
        random.shuffle(dupl_users)

        returned_ids = set()
        filtered_users = users_filt(dupl_users)
        for user in filtered_users:
            self.assertNotIn(user.id, returned_ids)
            returned_ids.add(user.id)
