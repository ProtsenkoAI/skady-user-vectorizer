from threading import Thread

from .crawl_runner import CrawlRunner


class BackgroundCrawler(CrawlRunner):
    def __init__(self, crawler: CrawlRunner):
        super().__init__()
        self.crawler = crawler
        self.run_thread = Thread(target=self.crawler.run)

    def run(self):
        self.run_thread.start()

    def stop(self):
        self.crawler.stop()
