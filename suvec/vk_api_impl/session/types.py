from typing import NamedTuple

from .records_managing.records import Proxy, Credentials

SessionData = NamedTuple("SessionData", [("creds", Credentials), ("proxy", Proxy)])
