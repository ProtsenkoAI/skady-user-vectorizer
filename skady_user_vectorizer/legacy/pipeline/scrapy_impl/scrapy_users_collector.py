from pipeline.interfaces import UsersCollector
from global_types import User
from data.list_users_storage import ListUsersStorage
from .scrapy_vk_spider import ScrapyVkSpider


from scrapy.crawler import CrawlerProcess, Settings


class ScrapyUsersCollector(UsersCollector):
    def __init__(self, settings: Settings,
                 ):
        self.crawler_settings = settings

    def run(self, start_user: User, need_to_obtain: int = 1000, nb_processed_friends: int = 10,
            ):
        # TODO: later can add other storages (and then use factories of storages or like that)
        users_storage = ListUsersStorage()
        process = CrawlerProcess(self.crawler_settings)
        process.crawl(ScrapyVkSpider, start_user=start_user, storage=users_storage,
                      nb_processed_friends=nb_processed_friends, users_needed=need_to_obtain)
        process.start()
        return users_storage.get_all()
