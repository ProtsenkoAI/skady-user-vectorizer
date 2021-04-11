from pipeline.interfaces import UsersCollector
from pipeline.interfaces import UsersStorage
from global_types import User, Users
from .scrapy_vk_spider import ScrapyVkSpider


from scrapy.crawler import CrawlerProcess, Settings


class ScrapyUsersCollector(UsersCollector):
    def __init__(self, settings: Settings,
                 ):
        self.crawler_settings = settings

    def start(self, start_user: User, users_storage: UsersStorage,
              need_to_obtain: int = 1000, nb_processed_friends: int = 10,
              ):
        # self.process.crawl(scrapy_info_retriever)
        process = CrawlerProcess(self.crawler_settings)
        process.crawl(ScrapyVkSpider, start_user=start_user, storage=users_storage,
                      nb_processed_friends=nb_processed_friends, users_needed=need_to_obtain)
        process.start()
