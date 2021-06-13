from typing import Any, NamedTuple, Union


RequestResult = Any
ErrorObj = NamedTuple("ErrorObj", [("code", Union[None, int]), ("error", Exception)])
