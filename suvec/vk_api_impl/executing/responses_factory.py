from suvec.common.executing import ResponsesFactoryImpl
from .parsers import VkApiFriendsParser, VkApiGroupsParser
from .data_retrieving import VkApiRequestDataRetriever, AioVkRequestDataRetriever


class VkApiResponsesFactory(ResponsesFactoryImpl):
    def __init__(self):
        super().__init__(VkApiFriendsParser(), VkApiGroupsParser(), VkApiRequestDataRetriever())


class AioVkResponsesFactory(ResponsesFactoryImpl):
    def __init__(self):
        super().__init__(VkApiFriendsParser(), VkApiGroupsParser(), AioVkRequestDataRetriever())
