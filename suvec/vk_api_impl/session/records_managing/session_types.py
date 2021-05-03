from typing import List, NamedTuple


Credentials = NamedTuple("Credentials", [("email", str), ("password", str)])
Proxy = NamedTuple("Proxy", [("address", str), ("protocols", List[str])])
