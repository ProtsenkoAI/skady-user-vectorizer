from typing import List
import json
import time

from interfaces import Credentials, Proxy
from .proxy_storage_interface import ProxyStorage
from .creds_storage_interface import CredsStorage
from .records import ProxyRecord, CredsRecord
from .db_types import ProxiesDict, CredsDict, UserProxyDict, UserCredsDict

from .consts import *


class ProxyAndCredsStorage(ProxyStorage, CredsStorage):
    # TODO: refactor (a lot of duplication)
    # TODO: need more convenient way for converting ProxiesDict -> ProxyRecord -> ProxiesDict
    # TODO: now will just rewrite content of save file when storage changes, later will need more efficient solution
    def __init__(self, save_pth: str):
        self.save_pth = save_pth
        with open(save_pth) as f:
            obj = json.load(f)

        self.proxies = self._parse_loaded_proxies(obj["proxies"])
        self.creds = self._parse_loaded_creds(obj["credentials"])

    def _parse_loaded_proxies(self, proxies_lst: List[ProxiesDict]) -> List[ProxyRecord]:
        res = []
        for idx, proxy_dict in enumerate(proxies_lst):
            proxy = proxy_dict["proxy"]
            if proxy_dict["status"] == PROXY_OK_STATUS:
                status_ok = True
                status_worked_out = False
            else:
                status_ok = False
                if proxy_dict["status"] == PROXY_WORKED_OUT_STATUS:
                    status_worked_out = True
                else:
                    status_worked_out = False

            time_since_last_change = time.time() - proxy_dict["status_change_time"]
            res.append(ProxyRecord(status_ok=status_ok, status_worked_out=status_worked_out,
                                   time_since_status_change=time_since_last_change,
                                   proxy=Proxy(address=proxy["address"], protocols=proxy["protocols"]),
                                   obj_id=idx))
        return res

    def _parse_loaded_creds(self, creds_lst: List[CredsDict]) -> List[CredsRecord]:
        res = []
        for idx, cred_dct in enumerate(creds_lst):
            creds = cred_dct["creds"]
            if cred_dct["status"] == CREDS_OK_STATUS:
                status_ok = True
                status_worked_out = False
            else:
                status_ok = False
                if cred_dct["status"] == CREDS_WORKED_OUT_STATUS:
                    status_worked_out = True
                else:
                    status_worked_out = False

            time_since_last_change = time.time() - cred_dct["status_change_time"]
            res.append(CredsRecord(status_ok=status_ok, status_worked_out=status_worked_out,
                                   time_since_status_change=time_since_last_change,
                                   creds=Credentials(email=creds["email"], password=creds["password"]),
                                   obj_id=idx))
        return res

    def get_proxy_records(self) -> List[ProxyRecord]:
        return self.proxies

    def set_proxy_worked_out(self, worked_out_proxy: ProxyRecord):
        for proxy in self.proxies:
            if worked_out_proxy.obj_id == proxy.obj_id:
                proxy.status_ok = False
                proxy.status_worked_out = True
                self._dump_state()
                break

    def get_creds_records(self) -> List[CredsRecord]:
        return self.creds

    def set_creds_worked_out(self, worked_out_creds: CredsRecord):
        for user_creds in self.creds:
            if worked_out_creds.obj_id == user_creds.obj_id:
                user_creds.status_ok = False
                user_creds.status_worked_out = True
                user_creds.time_since_status_change = 0
                self._dump_state()
                break

    def _dump_state(self):
        state = {"proxies": [], "credentials": []}
        for proxy in self.proxies:
            if proxy.status_ok:
                status = PROXY_OK_STATUS
            elif proxy.status_worked_out:
                status = PROXY_WORKED_OUT_STATUS
            else:
                raise ValueError(f"Unknown status of proxy. Proxy: {proxy}")
            status_change_time = int(time.time() - proxy.time_since_status_change)
            proxy_dct = ProxiesDict(status=status,
                                    status_change_time=status_change_time,
                                    proxy=UserProxyDict(address=proxy.proxy.address, protocols=proxy.proxy.protocols))
            state["proxies"].append(proxy_dct)

        for user_creds in self.creds:
            if user_creds.status_ok:
                status = CREDS_OK_STATUS
            elif user_creds.status_worked_out:
                status = CREDS_WORKED_OUT_STATUS
            else:
                raise ValueError(f"Unknown status of creds. Creds: {user_creds}")
            status_change_time = int(time.time() - user_creds.time_since_status_change)
            creds_dct = CredsDict(status=status,
                                  status_change_time=status_change_time,
                                  creds=UserCredsDict(email=user_creds.creds.email, password=user_creds.creds.password))
            state["credentials"].append(creds_dct)

        with open(self.save_pth, "w") as f:
            json.dump(state, f)
