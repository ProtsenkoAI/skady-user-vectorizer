import unittest
import guppy
import random
from typing import Callable, Optional

from suvec.common.postproc.data_managers.ram_data_manager import RAMDataManager, UsersData
from suvec.common.top_level_types import User, Group


class TestRAMDataManager(unittest.TestCase):
    def test_dumps_only_fully_parsed_users(self):
        """Adds some users, gets long term save and ensures that the save contains only users with all needed data
        """
        inspect_was_called = False
        nb_users_saved = 100
        friends_to_save = self._create_friends()
        groups_to_save = self._create_groups()

        def _inspect_save(save: UsersData):
            nonlocal inspect_was_called
            inspect_was_called = True

            self.assertEqual(len(save), nb_users_saved)
            for user_id, saved_data in save.items():
                self.assertIsNotNone(saved_data["friends"])
                self.assertIsNotNone(saved_data["groups"])

        mock_long_saver = MockLongTermSaver(_inspect_save)
        data_manager = RAMDataManager(long_term_saver=mock_long_saver, dmp_long_term_every=nb_users_saved)
        for user_id in range(nb_users_saved):
            user = User(user_id)

            data_manager.save_user_friends(user, friends_to_save)
            data_manager.save_user_groups(user, groups_to_save)

        self.assertTrue(inspect_was_called)

    def test_counts_fully_parsed(self):
        """Checks that data manager increases cnt_fully_parsed correctly"""
        data_manager = RAMDataManager(None, dmp_long_term_every=100)

        user1, user2, user3, user4 = [User(usr_id) for usr_id in range(4)]
        friends_to_save = self._create_friends()
        groups_to_save = self._create_groups()

        data_manager.save_user_friends(user1, friends_to_save)
        data_manager.save_user_friends(user2, friends_to_save)
        data_manager.save_user_groups(user3, groups_to_save)
        data_manager.save_user_friends(user4, friends_to_save)

        data_manager.save_user_groups(user1, groups_to_save)
        self.assertEqual(data_manager.cnt_fully_parsed, 1)

        data_manager.save_user_groups(user3, groups_to_save)  # saving groups again
        data_manager.save_user_groups(user2, groups_to_save)
        self.assertEqual(data_manager.cnt_fully_parsed, 2)

    def test_deletes_fully_parsed_from_mem(self):
        max_parsed_users_in_ram = 100
        groups_to_save = self._create_groups()
        friends_to_save = self._create_friends()

        data_manager = RAMDataManager(MockLongTermSaver(), dmp_long_term_every=max_parsed_users_in_ram)

        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size

        for fully_parsed_idx in range(max_parsed_users_in_ram * 100):
            user = User(fully_parsed_idx)
            data_manager.save_user_groups(user, groups_to_save)
            data_manager.save_user_friends(user, friends_to_save)

            if fully_parsed_idx % (max_parsed_users_in_ram * 10) == 0:
                memory_used = memory_checker.heap().size - memory_usage_before
                # 1000 bytes is some basic cost without any data
                self.assertLessEqual(memory_used, 1000)

    def test_memory_usage(self):
        """Adds a lot of users, both fully and non-fully parsed and checks memory usage"""
        data_manager = RAMDataManager(MockLongTermSaver(), dmp_long_term_every=10 ** 8)
        memory_checker = guppy.hpy()
        memory_usage_before = memory_checker.heap().size
        bytes_per_user = 20
        nb_friends = 10
        nb_groups = 10
        bytes_for_friends = nb_friends * 4
        bytes_for_groups = nb_groups * 4

        nb_unpaired_users = 10 ** 3
        for not_fully_parsed_idx in range(nb_unpaired_users):
            user = User(not_fully_parsed_idx)

            if not_fully_parsed_idx % 2:
                data_manager.save_user_groups(user, self._create_groups(nb_groups))
            else:
                data_manager.save_user_friends(user, self._create_friends(nb_friends))

        memory_used = memory_checker.heap().size - memory_usage_before

        self.assertLessEqual(memory_used, nb_unpaired_users * (bytes_per_user + bytes_for_friends + bytes_for_groups))

    def _create_friends(self, nb=2):
        start_idx = random.randint(10 ** 6, 10 ** 7)
        return [User(usr_id) for usr_id in range(start_idx, start_idx + nb)]

    def _create_groups(self, nb=2):
        start_idx = random.randint(10 ** 6, 10 ** 7)
        return [Group(group_id) for group_id in range(start_idx, start_idx + nb)]

    def test_doesnt_save_user_long_term_twice(self):
        # TODO
        ...


class MockLongTermSaver:
    def __init__(self, save_callback: Optional[Callable] = None):
        if save_callback is None:
            save_callback = self._do_nothing
        self.callback = save_callback

    def _do_nothing(self, *args, **kwargs):
        pass

    def save(self, data: UsersData):
        self.callback(data)
