from typing import Dict, TypedDict, List, Optional
from suvec.common.top_level_types import User, Group


class UserData(TypedDict):
    friends: Optional[List[User]]
    groups: Optional[List[Group]]


UsersData = Dict[str, UserData]
