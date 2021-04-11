from pipeline.scrapy_impl.scrapy_users_collector import ScrapyUsersCollector
from util import read_config
from parsing import MockInfoRetriever
from data.list_users_storage import ListUsersStorage
from scrapy.crawler import Settings
from global_types import User

if __name__ == "__main__":
    info_retriever = MockInfoRetriever(read_config())
    users_storage = ListUsersStorage()
    user = User("https://vk.com/gushchin_d")
    ScrapyUsersCollector(Settings({"COOKIES_ENABLED": True, "DOWNLOAD_DELAY": 1})).start(user, users_storage, 1000, 100)
    print(users_storage.get_all()[:10])
