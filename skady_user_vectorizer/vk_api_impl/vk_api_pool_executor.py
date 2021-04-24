from typing import List
from .requests import Request
from .responses import Response


class VkApiPoolExecutor:
    def execute(self, requests: List[Request]) -> Response:
        raise NotImplementedError
