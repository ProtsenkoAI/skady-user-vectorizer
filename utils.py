from pathlib import Path
from typing import List
import json


def get_resources_path(settings_pth: str) -> Path:
    settings = get_res_settings(settings_pth)
    res_path = Path(settings_pth).parent / settings["res_path"]
    return res_path


def get_proxy_and_creds_paths(settings_pth: str) -> List[str]:
    access_path = get_resources_path(settings_pth) / "access"
    proxy = str(access_path / "proxies.json")
    creds = str(access_path / "creds.json")
    return [proxy, creds]


def get_data_requester_checkpoint_paths(settings_pth: str) -> List[str]:
    checkp_settings = get_res_settings(settings_pth)["checkpoints"]
    checkp_dir = get_resources_path(settings_pth) / "checkpoints"
    data_checkp = checkp_dir / checkp_settings["data_checkpoint"]
    req_checkp = checkp_dir / checkp_settings["requester_checkpoint"]
    return [data_checkp, req_checkp]


def get_result_path(settings_pth: str) -> str:
    res_settings = get_res_settings(settings_pth)
    result = get_resources_path(settings_pth) / res_settings["result_file"]
    return result


def get_res_settings(settings_pth: str) -> dict:
    return json.load(open(settings_pth))["resources"]


def get_backups_path(settings_pth: str) -> Path:
    res_pth = get_resources_path(settings_pth)
    return res_pth / "backups"
