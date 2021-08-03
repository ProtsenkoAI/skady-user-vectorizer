# pseudocode
import json
import vk_api
import requests

user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'


def get_resources():
    # TODO: logs
    creds_pth = "/home/arseny/Projects/skady-user-vectorizer/resources/access/creds.json"
    proxy_pth = "/home/arseny/Projects/skady-user-vectorizer/resources/access/Webshare 10 proxies.txt"

    with open(creds_pth) as f:
        creds_data = json.load(f)

    with open(proxy_pth) as f:
        proxies = f.read().split("\n")
    proxies = [proxy for proxy in proxies if proxy != ""]

    print(proxies)

    creds = []
    for record in creds_data:
        creds.append(record["creds"])

    print(creds)

    return creds, proxies


def create_sessions(creds, proxies, session_loop: int):
    # TODO: logs
    working_creds = []
    for cred in creds:
        try:
            session = vk_api.vk_api.VkApi(login=cred['email'], password=cred["password"])
            session.auth()
            req_res = session.method("friends.get", values={"user_id": 1})
            working_creds.append(cred)
            if len(working_creds) == 10:
                break
        except Exception as e:
            print("cred exception: ", e)
            pass

    # simplest realisation: doesn't change sessions between loops

    sessions = list(zip(working_creds, proxies[:10]))
    return sessions


def use_session(session):
    # TODO: logs
    # TODO: use vk session
    creds, proxy = session

    s = requests.Session()
    s.headers.update({'User-agent': user_agent})
    for proxy_protocol in ["http", "https"]:
        s.proxies.update({proxy_protocol: proxy})

    vk_session = vk_api.VkApi(creds["email"], creds["password"], session=s)
    vk_session.auth()

    print("BEBEBABA using vk session")


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
