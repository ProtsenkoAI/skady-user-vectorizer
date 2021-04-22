from pipeline.scrapy_impl.scrapy_users_collector import ScrapyUsersCollector
from util import read_config
from parsing import MockInfoRetriever
from scrapy.crawler import Settings
from global_types import User

if __name__ == "__main__":
    info_retriever = MockInfoRetriever(read_config())
    user = User("https://vk.com/gushchin_d")
    collected_users = ScrapyUsersCollector(Settings({"COOKIES_ENABLED": True, "DOWNLOAD_DELAY": 1})
                                           ).run(user, 1000, 100)
    print(collected_users[:10])
