from typing import NamedTuple, List


User = NamedTuple("User", [("id", str)])
Group = NamedTuple("Group", [("id", str)])
Credentials = NamedTuple("Credentials", [("email", str), ("password", str)])


Proxy = NamedTuple("Proxy", [("address", str), ("protocols", List[str])])
