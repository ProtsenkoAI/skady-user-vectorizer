import unittest
from suvec.common.requesting import EconomicRequester, DuplicateUsersFilter, RequestedUsersFileStorage
from suvec.common.top_level_types import User
from suvec.vk_api_impl.requesting import VkApiRequestsCreator
from suvec.vk_api_impl.requesting.requests import FriendsRequest, GroupsRequest
from utils import get_resources_path


class TestEcoRequester(unittest.TestCase):
    def test_access_error(self):
        """Test that if access error occurred on user in will be requested again later"""
        requester = self._create()
        some_users = [User(1), User(2), User(3)]
        requester.add_users(some_users)

        requests = requester.get_requests()
        for request in requests:
            if request.user.id in [1, 2]:
                requester.request_succeed(request.user, request.req_type)
            else:
                requester.access_error_occurred(request)

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

    def test_functional_adding_and_getting_users(self):
        """Makes few cycles of add_users, get_requests, request_succeeded to imitate real operations"""
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

    def _create(self):
        test_res_pth = get_resources_path("./settings.json") / "testing"
        users_to_friends_req = RequestedUsersFileStorage(test_res_pth / "users_to_friends_request.txt")
        users_to_groups_req = RequestedUsersFileStorage(test_res_pth / "users_to_groups_request.txt")
        requester = EconomicRequester(VkApiRequestsCreator(),
                                      friends_req_storage=users_to_friends_req,
                                      groups_req_storage=users_to_groups_req,
                                      users_filter=DuplicateUsersFilter(),
                                      max_requests_per_call=100)
        return requester

