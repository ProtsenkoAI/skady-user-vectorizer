from abc import ABC, abstractmethod


class ParseResProcessor:
    def process_parsed_friends(self, user_friends_response: Response):
        user_friends_parsing_result = self.info_retriever.get_friends(user_friends_response)
        parse_status = user_friends_parsing_result.status

        if parse_status == SUCCESS:
            self.storage_manager.save_user_friends(user_friends_parsing_result)
            self._check_must_stop_crawl()
            self.requests_creator.add_users(user_friends_parsing_result.friends)
            new_requests = self.requests_creator.get_new_requests()
            yield from new_requests
        else:
            self._process_unsuccessful_parse(user_friends_parsing_result)

    def process_parsed_groups(self, user_groups_response: Response):
        user_groups_parse_res = self.info_retriever.get_groups(user_groups_response)
        parse_status = user_groups_parse_res.status
        if parse_status == SUCCESS:
            self.storage_manager.save_user_groups(user_groups_parse_res)
        else:
            self._process_unsuccessful_parse(user_groups_parse_res)

    def _process_unsuccessful_parse(self, parse_res):  # TODO: add typing
        if parse_res.status == NEED_TO_STOP_PARSING:
            self._close_spider("The error due to which crawling has to be stopped occurred")
        self._logger.log_parse_error(parse_res.status, parse_res.desc)

    def _check_must_stop_crawl(self):
        nb_users_parsed = self.storage_manager.get_num_users()
        if nb_users_parsed >= self.users_needed:
            self._logger.log_info("Parsed enough users, stopping crawl")
            self._close_spider(f"Parsed {nb_users_parsed}, stopping crawling")

    def _close_spider(self, msg):
        raise CloseSpider(msg)

