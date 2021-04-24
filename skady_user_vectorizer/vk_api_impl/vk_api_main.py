from .vk_api_crawl_runner import VkApiCrawlRunner


def run():
    runner = VkApiCrawlRunner()
    runner.run()


if __name__ == "__main__":
    run()
