import json
import os
import signal

from ..top_level_types import User
from .economic_requester import EconomicRequester


class RequesterCheckpointer:
    # TODO: refactor
    def __init__(self, checkpoint_pth: str):
        self.checkpoint_pth = checkpoint_pth

    def load_checkpoint(self, requester: EconomicRequester):
        # TODO: add additional methods to chek that save exists
        if os.path.isfile(self.checkpoint_pth):
            with open(self.checkpoint_pth) as f:
                friends_requests_ids, groups_requests_ids, already_seen_ids = json.load(f)

            friends_requests_users = [User(id=user_id) for user_id in friends_requests_ids]
            groups_requests_users = [User(id=user_id) for user_id in groups_requests_ids]
            requester.users_to_friends_request += friends_requests_users
            requester.users_to_groups_request += groups_requests_users
            requester.already_added.update(already_seen_ids)
        else:
            with open(self.checkpoint_pth, "w") as f:
                default_val = ([], [], [])
                json.dump(default_val, f)

    def save_checkpoint(self, requester: EconomicRequester):
        friends_requests_ids = [user.id for user in requester.users_to_friends_request]
        groups_requests_ids = [user.id for user in requester.users_to_groups_request]
        checkpoint = friends_requests_ids, groups_requests_ids, list(requester.already_added)

        # prevent terminating while writing
        self._need_to_stop = False
        signal.signal(signal.SIGTERM, self._wait_till_write_end)
        with open(self.checkpoint_pth, "w") as f:
            json.dump(checkpoint, f)
        if self._need_to_stop:
            signal.raise_signal(signal.SIGTERM)

    def _wait_till_write_end(self):
        self._need_to_stop = True
