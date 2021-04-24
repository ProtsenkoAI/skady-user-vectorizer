from typing import NamedTuple, Any


User = NamedTuple("User", [("id", str)])
Group = NamedTuple("Group", [("id", str)])
Credentials = NamedTuple("Credentials", [("email", str), ("password", str)])
