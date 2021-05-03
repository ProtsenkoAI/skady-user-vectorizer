from typing import Any, NamedTuple, Union


RequestResult = Any
ErrorObj = NamedTuple("VkApiErrorObj", [("code", Union[None, int]), ("error", Exception)])
ResponseObj = NamedTuple("ResponseObj", [("value", Union[ErrorObj, dict]), ("is_error", bool)])
