from datetime import datetime
from typing import Optional
import json
from time import time

log_pth = f"/home/arseny/Projects/skady-user-vectorizer/resources/logs/playground_{int(time())}.jsonl"


def log_session_created(proxy, creds):
    log("session_created", proxy, creds)


def log_forming_session(creds, proxy):
    log("forming session", proxy, creds)


def log_captcha_needed_error(proxy, creds, error_info: str, req_type=None):
    log("captcha_error", proxy, creds, error_info, req_type=req_type)


def log_access_error(proxy, creds, error_info: str, req_type=None):
    log("access_error", proxy, creds, error_info, req_type=req_type)


def log_request_success(proxy, creds, used_pool=False, req_type=None):
    log("request_success", proxy, creds, other_info=f"Pool={used_pool}", req_type=req_type)


def log_bad_password(proxy, creds, error_info):
    log("bad password", proxy, creds, other_info=error_info)


def log(event_type: str, proxy: str, creds: dict, other_info: Optional[str] = None, **kwargs):
    timestamp = str(datetime.now())
    logged_data = {"time": timestamp, "event_type": event_type, "proxy": proxy, "creds": creds, "info": other_info,
                   **kwargs}
    with open(log_pth, "a") as f:
        f.write(json.dumps(logged_data) + "\n")
