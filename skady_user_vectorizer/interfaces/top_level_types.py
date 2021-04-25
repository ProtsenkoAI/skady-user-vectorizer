from typing import NamedTuple, TypedDict, List


User = NamedTuple("User", [("id", str)])
Group = NamedTuple("Group", [("id", str)])
Credentials = NamedTuple("Credentials", [("email", str), ("password", str)])


class Proxy(TypedDict):
    address: str
    protocols: List[str]
