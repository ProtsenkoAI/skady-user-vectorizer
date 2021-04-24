# TODO: maybe split the module
from abc import ABC, abstractmethod


class Request(ABC):
    ...


class FriendsRequest(Request):
    ...


class GroupsRequest(Request):
    ...
