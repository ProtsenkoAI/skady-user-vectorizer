# TODO: need to create better files structure
from vk_api_impl.vk_api_crawl_runner import VkApiCrawlRunner


def run():
    runner = VkApiCrawlRunner(start_user_id="213167272",
                              path_to_creds="../creds.json",
                              path_to_proxies="../proxies.json")
    runner.run()


if __name__ == "__main__":
    run()
