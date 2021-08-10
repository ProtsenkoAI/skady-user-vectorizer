from vk_api.requests_pool import RequestResult
from suvec.common.executing import ErrorObj
from aiovk.pools import AsyncResult


class VkApiRequestDataRetriever:
    @staticmethod
    def get_resp_data(raw_resp: RequestResult):
        return raw_resp.result["items"]

    @staticmethod
    def get_error(raw_resp: RequestResult) -> ErrorObj:
        if raw_resp.error is not False:
            return ErrorObj(code=raw_resp.error["error_code"], error=raw_resp.error)


class AioVkRequestDataRetriever:
    # NOTE: it's identical to VkApiRequestDataRetriever by coincidence (two libraries have same behaviour)
    @staticmethod
    def get_resp_data(raw_resp: AsyncResult):
        return raw_resp.result["items"]

    @staticmethod
    def get_error(raw_resp: AsyncResult) -> ErrorObj:
        if raw_resp.error is not None:
            return ErrorObj(code=raw_resp.error["error_code"], error=raw_resp.error)
