from typing import List, Tuple
import json

from interfaces import Credentials, Proxy


def read_proxies_and_creds(proxy_pth: str, creds_pth: str) -> Tuple[List[Proxy], List[Credentials]]:
    with open(proxy_pth) as f:
        proxies = json.load(f)
    with open(creds_pth) as f:
        creds_raw = json.load(f)
        creds = [Credentials(*creds) for creds in creds_raw]
    return proxies, creds
