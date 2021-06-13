from suvec.common.requesting import Request


class FriendsRequest(Request):
    def get_method(self) -> str:
        return "friends.get"


class GroupsRequest(Request):
    def get_method(self) -> str:
        return "groups.get"
