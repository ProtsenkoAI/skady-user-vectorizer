"""Take 100 proxies and one account, authorize 3 times per proxy and check for Captcha needed errors"""

from time import sleep
import requests
import vk_api
import traceback
from vk_api import exceptions as vk_excepts

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

    return creds, proxies


all_creds, proxies = get_resources()
proxy = proxies[-4]

credentials = all_creds
del all_creds

for loop in range(10):
    for creds in credentials:
        s = requests.Session()
        s.headers.update({'User-agent': user_agent})
        for proxy_protocol in ["http", "https"]:
            s.proxies.update({proxy_protocol: proxy})

        vk_session = vk_api.VkApi(creds["email"], creds["password"], session=s)
        requests_pool = vk_api.VkRequestsPool(vk_session)
        try:
            vk_session.auth()
            log_session_created(proxy, creds)
        except vk_excepts.Captcha as e:
            log_captcha_needed_error(proxy, creds, traceback.format_exc())
        except vk_excepts.BadPassword as e:
            log_bad_password(proxy, creds, traceback.format_exc())
            credentials.remove(creds)
        sleep(1)
