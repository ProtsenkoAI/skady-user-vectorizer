import unittest
import guppy
from typing import Callable

from suvec.common.postproc.data_managers.ram_data_manager import RAMDataManager, UsersData
from suvec.common.top_level_types import User, Group

friends_to_save = [User(1), User(2)]
groups_to_save = [Group(1), Group(2)]


class TestRAMDataManager(unittest.TestCase):
    def test_dumps_only_fully_parsed_users(self):
        """Adds some users, gets long term save and ensures that the save contains only users with all needed data
        """
        inspect_was_called = False
        nb_users_saved = 100

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

        data_manager.save_user_friends(user1, friends_to_save)
        data_manager.save_user_friends(user2, friends_to_save)
        data_manager.save_user_groups(user3, groups_to_save)
        data_manager.save_user_friends(user4, friends_to_save)

        data_manager.save_user_groups(user1, groups_to_save)
        self.assertEqual(data_manager.cnt_fully_parsed, 1)

        data_manager.save_user_groups(user3, groups_to_save)  # saving groups again
        data_manager.save_user_groups(user2, groups_to_save)
        self.assertEqual(data_manager.cnt_fully_parsed, 2)

    def test_memory_usage(self):
        """Adds a lot of users, both fully and non-fully parsed and checks memory usage"""
        # TODO: split this test
        max_parsed_users_in_ram = 100
        bytes_per_user = 38

        def _do_nothing(*args, **kwargs):
            pass

        data_manager = RAMDataManager(MockLongTermSaver(_do_nothing), dmp_long_term_every=max_parsed_users_in_ram)

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

        start_idx = max_parsed_users_in_ram * 100
        for not_fully_parsed_idx in range(start_idx, start_idx + 10 ** 3):
            user = User(not_fully_parsed_idx + start_idx)

            if not_fully_parsed_idx % 2:
                data_manager.save_user_groups(user, groups_to_save)
            else:
                data_manager.save_user_friends(user, friends_to_save)

        memory_used = memory_checker.heap().size - memory_usage_before

        basic_dict_cost = 240
        hashtable_cost_coef = 1.6
        self.assertLessEqual(memory_used, hashtable_cost_coef * 10 ** 3 * (bytes_per_user + basic_dict_cost))


class MockLongTermSaver:
    def __init__(self, save_callback: Callable):
        self.callback = save_callback

    def save(self, data: UsersData):
        self.callback(data)
