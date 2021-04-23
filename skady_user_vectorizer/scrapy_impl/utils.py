from typing import Type
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess, Settings


def run_crawl(spider: Type[Spider], *spider_args, **spider_kwargs):
    # TODO: set settings from another place
    settings = Settings({"COOKIES_ENABLED": True,
                         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                       '(KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
                         })
    process = CrawlerProcess(settings)
    process.crawl(spider, *spider_args, **spider_kwargs)
    process.start()
