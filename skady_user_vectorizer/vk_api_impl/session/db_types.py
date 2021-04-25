from typing import TypedDict, List


class UserCredsDict(TypedDict):
    email: str
    password: str


class UserProxyDict(TypedDict):
    address: str
    protocols: List[str]


class CredsDict(TypedDict):
    status: str
    status_change_time: int
    creds: UserCredsDict


class ProxiesDict(TypedDict):
    status: str
    status_change_time: int
    proxy: UserProxyDict
