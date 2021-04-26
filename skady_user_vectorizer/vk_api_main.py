from vk_api_impl.vk_api_crawl_runner import VkApiCrawlRunner


def run():
    runner = VkApiCrawlRunner(start_user_id="213167272",
                              proxies_save_pth="../proxies.json",
                              creds_save_pth="../creds.json"
                              )
    runner.run()


if __name__ == "__main__":
    run()
