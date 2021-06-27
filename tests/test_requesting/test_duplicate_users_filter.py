import unittest
import guppy
import random
import time

from suvec.common.requesting import DuplicateUsersFilter
from suvec.common.top_level_types import User


class TestDuplicateUsersFilter(unittest.TestCase):
    def test_memory_usage(self):
        """Performs a lot of filtering on many users and checks memory usage"""
        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size
        bytes_per_user = 4  # a lot of memory because of py objects and hashmap of added users
        users_nb = 10 ** 6
        step = 10 ** 5
        additional_mem = 1000  # for objects etc.

        users_filt = DuplicateUsersFilter()
        for start_user_id in range(0, users_nb, step):
            users = self._create_users(start_user_id, start_user_id + step)
            users_filt(users)
        del users

        memory_used_by_filter = memory_checker.heap().size - memory_usage_before
        self.assertLess(memory_used_by_filter, users_nb * bytes_per_user + additional_mem)

    def test_unique_users(self):
        """Checks that no user can be returned twice"""

        users_filt = DuplicateUsersFilter()

        dupl_users = self._create_users()
        dupl_users += self._create_users()
        random.shuffle(dupl_users)
        returned_ids = set()
        filtered_users = users_filt(dupl_users)
        for user in filtered_users:
            self.assertNotIn(user.id, returned_ids)
            returned_ids.add(user.id)

    def test_speed(self):
        users_per_sec = 10 ** 5
        nb_users = 10 ** 4
        users_filt = DuplicateUsersFilter()
        some_users = self._create_users(end=nb_users)
        _ = users_filt(some_users)

        start_time = time.time()
        _ = self._create_users(start=0.5 * nb_users, end=1.5 * nb_users)
        time_to_filt = time.time() - start_time
        # print(f"Time to filter {nb_users} users: {time_to_filt} s")
        self.assertLessEqual(time_to_filt, nb_users / users_per_sec)

    def test_checkpointing(self):
        """Checkpoints filter, loads from checkpoint and checks that it works properly"""
        nb_users = 10 ** 2
        users_filt = DuplicateUsersFilter()
        some_users = self._create_users(end=nb_users)

        users_filtered_before_checkp = users_filt(some_users)

        checkpoint = users_filt.get_checkpoint()
        del users_filt
        new_users_filt = DuplicateUsersFilter()
        new_users_filt.load_checkpoint(checkpoint)

        new_users = self._create_users(start=nb_users, end=2 * nb_users)
        new_filtered_users = new_users_filt(new_users)

        final_users_to_check_that_checkp_worked = self._create_users(start=0, end=3 * nb_users)
        final_users_filtered = new_users_filt(final_users_to_check_that_checkp_worked)

        all_filtered_before = [*users_filtered_before_checkp, *new_filtered_users]
        for user in final_users_filtered:
            self.assertNotIn(user, all_filtered_before)

        self.assertEqual(len(final_users_filtered), nb_users)  # check that didn't filtered not-met-before users

    def _create_users(self, start=0, end=10 ** 3):
        start = int(start)
        end = int(end)
        return [User(usr_id) for usr_id in range(start, end)]
