import util
from .scrapy_crawl_runner import ScrapyVkCrawlRunner


def run():
    config = util.read_config()
    runner = ScrapyVkCrawlRunner(config, user_id="371492632")
    runner.run()
    # just instantiate spider with all needed objects


if __name__ == "__main__":
    run()
