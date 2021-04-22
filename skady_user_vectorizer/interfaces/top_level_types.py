from typing import NamedTuple, Any


User = NamedTuple("User", [("id", str)])
Group = Any  # TODO: make some fields for groups
Credentials = NamedTuple("Credentials", [("email", str), ("password", str)])
