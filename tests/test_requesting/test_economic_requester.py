import unittest
import shutil
import os
from suvec.common.requesting import EconomicRequester, DuplicateUsersFilter, RequestedUsersFileStorage
from suvec.common.top_level_types import User
from suvec.vk_api_impl.requesting import VkApiRequestsCreator
from suvec.vk_api_impl.requesting.requests import FriendsRequest, GroupsRequest
from utils import get_resources_path

test_res_pth = get_resources_path("./settings.json") / "testing"


class TestEcoRequester(unittest.TestCase):
    # TODO: test that don't lose data in checkpointing process
    def test_error_processing(self):
        """Test that if access error occurred on user in will be requested again later"""
        requester = self._create()
        some_users = [User(1), User(2), User(3)]
        requester.add_users(some_users)

        requests = requester.get_requests()
        for request in requests:
            if request.user.id in [1, 2]:
                requester.request_succeed(request.user, request.req_type)
            else:
                requester.user_unrelated_error(request)

        new_requests = requester.get_requests()
        groups_request_users = []
        friends_request_users = []
        for request in new_requests:
            if isinstance(request, FriendsRequest):
                friends_request_users.append(request.user.id)
            else:
                groups_request_users.append(request.user.id)
        # users 1 and 2 marked as successful so we move to second (groups) request. request for 3 user failed thus we
        #   try friends request again
        self.assertIn(1, groups_request_users)
        self.assertIn(2, groups_request_users)
        self.assertIn(3, friends_request_users)

    def test_low_number_of_not_fully_parsed_users(self):
        """Makes a lot of loops and checks that requester doesn't generate number of non-fully parsed users larger,
        than max_requests_per_call param value.
        Non-fully-parsed users are users with only one requested made - only groups or only friends"""
        users_groups_req_made, users_friends_req_made = set(), set()
        users_to_request = [User(usr_id) for usr_id in range(10 ** 5)]
        add_users_step = 10 ** 4

        max_requests = 500
        requester = self._create(max_requests)

        while users_to_request:
            chosen_users = users_to_request[:add_users_step]
            users_to_request = users_to_request[add_users_step:]
            requester.add_users(chosen_users)
            requests = requester.get_requests()

            for request in requests:
                requester.request_succeed(request.user, request.req_type)
                if request.req_type == "friends":
                    users_friends_req_made.add(request.user)
                else:
                    users_groups_req_made.add(request.user)

            # users only in one set
            unpaired_users_nb = len(users_groups_req_made.symmetric_difference(users_friends_req_made))

            self.assertLessEqual(unpaired_users_nb, max_requests)

    def test_functional_adding_and_getting_users(self):
        """Makes few loops of add_users, get_requests, request_succeeded to imitate real operations"""
        requester = self._create()
        some_users = [User(1), User(2), User(3)]

        requester.add_users(some_users)
        requests = requester.get_requests()

        # need 3 friends requests first, when they'll be marked as successful, should return 3 groups requests first
        for request in requests:
            self.assertIsInstance(request, FriendsRequest)
            requester.request_succeed(request.user, req_type=request.req_type)

        # adding some new users, but their requests should be made only after friends requests for some_users
        new_users = [User(4), User(5), User(6)]
        requester.add_users(new_users)

        requests = requester.get_requests()
        groups_requests_of_old_users = requests[:len(some_users)]
        new_requests = requests[len(some_users):]

        for request in groups_requests_of_old_users:
            self.assertIsInstance(request, GroupsRequest)
            self.assertIn(request.user, some_users)

        for request in new_requests:
            self.assertIsInstance(request, FriendsRequest)
            self.assertIn(request.user, new_users)

    def _create(self, max_requests_nb: int = 100):
        users_to_friends_req = RequestedUsersFileStorage(test_res_pth / "users_to_friends_request.txt")
        users_to_groups_req = RequestedUsersFileStorage(test_res_pth / "users_to_groups_request.txt")
        requester = EconomicRequester(VkApiRequestsCreator(),
                                      friends_req_storage=users_to_friends_req,
                                      groups_req_storage=users_to_groups_req,
                                      users_filter=DuplicateUsersFilter(),
                                      max_requests_per_call=max_requests_nb)
        return requester

    def tearDown(self):
        shutil.rmtree(test_res_pth)
        os.mkdir(test_res_pth)
