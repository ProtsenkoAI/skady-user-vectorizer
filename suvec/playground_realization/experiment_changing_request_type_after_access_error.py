import vk_api
import traceback
import requests
from time import sleep
from random import shuffle

from experiments_logs import *

user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'


def get_resources():
    creds_pth = "/home/arseny/Projects/skady-user-vectorizer/resources/access/creds.json"
    proxy_pth = "/home/arseny/Projects/skady-user-vectorizer/resources/access/Webshare 100 proxies.txt"

    with open(creds_pth) as f:
        creds_data = json.load(f)

    with open(proxy_pth) as f:
        proxies = f.read().split("\n")
    proxies = [proxy for proxy in proxies if proxy != ""]

    print(proxies)

    creds = []
    for record in creds_data:
        creds.append(record["creds"])

    return creds[30: 30 + 10], proxies[30:60]


def _make_friends_request(vk_session):
    return vk_session.method("friends.get", values={"user_id": 1})


creds_to_last_usage_time = {}


def create_sessions(creds, proxies, session_loop_idx: int):
    used_proxies = proxies.copy()
    shuffle(used_proxies)

    if session_loop_idx == 0:
        req_type = "friends.get"
    else:
        req_type = "groups.get"

    sessions = []
    proxy_per_cred = 3
    proxy_groups = [proxies[start_idx: start_idx + proxy_per_cred] for start_idx in
                    range(0, len(proxies), proxy_per_cred)]

    for cred, proxies_for_cred in zip(creds, proxy_groups):
        proxy = proxies_for_cred[session_loop_idx % len(proxies_for_cred)]
        sessions.append((cred, proxy, req_type))
        log_forming_session(cred, proxy)
    else:
        log("run out of resources", None, None)

    return sessions


def use_session(session):
    creds, proxy, req_type = session

    if creds["email"] + creds["password"] in creds_to_last_usage_time:
        last_use = creds_to_last_usage_time[creds["email"] + creds["password"]]
        min_to_wait = 65
        need_to_wait = 60 * min_to_wait + last_use - time()
        if need_to_wait > 0:
            log("sleep", None, None, f"time={need_to_wait}")
            sleep(need_to_wait)

    s = requests.Session()
    s.headers.update({'User-agent': user_agent})
    for proxy_protocol in ["http", "https"]:
        s.proxies.update({proxy_protocol: proxy})

    vk_session = vk_api.VkApi(creds["email"], creds["password"], session=s)
    requests_pool = vk_api.VkRequestsPool(vk_session)
    try:
        vk_session.auth()
        sleep(1)

    except Exception as e:
        log_captcha_needed_error(proxy, creds, traceback.format_exc())
    else:
        log_session_created(proxy, creds)
        while True:
            try:
                for _ in range(25):
                    resp = requests_pool.method(req_type, values={"user_id": 1})
                requests_pool.execute()
                if resp.error:
                    log_access_error(proxy, creds, resp.error, req_type=req_type)
                    break

                # _make_friends_request(vk_session)
                log_request_success(proxy, creds, used_pool=True, req_type=req_type)
            except Exception as e:
                log_access_error(proxy, creds, traceback.format_exc())
                break


    creds_to_last_usage_time[creds["email"] + creds["password"]] = time()


def need_terminate_scraping(session_loop_idx):
    return session_loop_idx == 2


creds, proxies = get_resources()

sessions_generation_loop_idx = 0

while True:
    if need_terminate_scraping(sessions_generation_loop_idx):
        break

    sessions = create_sessions(creds, proxies, sessions_generation_loop_idx)  # can sleep if run out of sessions

    for session in sessions:
        use_session(session)

    sessions_generation_loop_idx += 1