from typing import TypedDict


class UserCredsDict(TypedDict):
    email: str
    password: str


class UserProxyDict(TypedDict):
    address: str


class AuthResourceDict(TypedDict):
    status: str
    status_change_time: int


class CredsDict(AuthResourceDict):
    creds: UserCredsDict


class ProxyDict(AuthResourceDict):
    proxy: UserProxyDict
