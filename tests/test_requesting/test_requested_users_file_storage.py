import unittest
import os
import guppy
import sys

from suvec.common.requesting import RequestedUsersFileStorage
from suvec.common.top_level_types import User
from utils import get_resources_path


class TestRequestedUsersFileStorage(unittest.TestCase):
    def setUp(self):
        """Delete existing storage"""
        storage_pth = self._get_storage_pth()
        if os.path.isfile(storage_pth):
            os.remove(storage_pth)

    def test_memory_usage(self):
        """Adding a lot of users and check that memory usage is low"""
        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size
        users_storage = self._create_storage()

        for idx in range(10 ** 6):
            user = User(idx)
            users_storage.add_user(user)
            if idx % 10 ** 5 + 5 == 0:
                memory_bytes_usage = memory_checker.heap().size
                # memory usage should be enough to store 10 ** 3 ram users and 10 ** 3 users scheduled for dump
                nb_users_storing = 2 * 10 ** 3
                bytes_per_user = 36
                self.assertLess(memory_bytes_usage - memory_usage_before, nb_users_storing * bytes_per_user + 1000)

    def test_get_all_added_users(self):
        """Add a lot of users and check that everyone will be retrieved back"""
        users_storage = self._create_storage()
        users_added = set()
        for idx in range(10 ** 5):
            user = User(idx)
            users_added.add(user)
            users_storage.add_user(user)

        one_iter_users_nb = 10 ** 4
        for _ in range(len(users_added) // one_iter_users_nb):
            users = users_storage.get_users(one_iter_users_nb)
            users_added.difference_update(users)

        self.assertEqual(len(users_added), 0)  # if 0, all users were retrieved

    def _create_storage(self):
        return RequestedUsersFileStorage(self._get_storage_pth(),
                                         max_users_storing=10 ** 3, save_unused_users_every=10 ** 3)

    def _get_storage_pth(self):
        return get_resources_path("./settings.json") / "testing" / f"some_users_storage.txt"
