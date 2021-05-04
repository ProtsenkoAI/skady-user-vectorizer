import json
import os

from ..top_level_types import User
from .base_requester_impl import BaseRequesterImpl


class RequesterCheckpointer:
    def __init__(self, checkpoint_pth: str):
        self.checkpoint_pth = checkpoint_pth

    def load_checkpoint(self, requester: BaseRequesterImpl):
        # TODO: add additional methods to chek that save exists
        if os.path.isfile(self.checkpoint_pth):
            with open(self.checkpoint_pth) as f:
                friends_requests_ids, groups_requests_ids = json.load(f)

            friends_requests_users = [User(id=user_id) for user_id in friends_requests_ids]
            groups_requests_users = [User(id=user_id) for user_id in groups_requests_ids]
            requester.users_to_friends_request += friends_requests_users
            requester.users_to_groups_request += groups_requests_users

    def save_checkpoint(self, requester: BaseRequesterImpl):
        friends_requests_ids = [user.id for user in requester.users_to_friends_request]
        groups_requests_ids = [user.id for user in requester.users_to_groups_request]
        checkpoint = friends_requests_ids, groups_requests_ids
        with open(self.checkpoint_pth, "w") as f:
            json.dump(checkpoint, f)
