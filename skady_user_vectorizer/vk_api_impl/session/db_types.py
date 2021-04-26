from typing import TypedDict, List


class UserCredsDict(TypedDict):
    email: str
    password: str


class UserProxyDict(TypedDict):
    address: str
    protocols: List[str]


class AuthResourceDict(TypedDict):
    status: str
    status_change_time: int
    obj_id: int


class CredsDict(AuthResourceDict):
    creds: UserCredsDict


class ProxyDict(AuthResourceDict):
    proxy: UserProxyDict
