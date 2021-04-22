from typing import Type
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess, Settings


def run_crawl(spider: Type[Spider], *spider_args, **spider_kwargs):
    # TODO: set settings from another place
    settings = Settings({"COOKIES_ENABLED": True})
    process = CrawlerProcess(settings)
    process.crawl(spider, *spider_args, **spider_kwargs)
    process.start()
