from typing import TypedDict
from datetime import datetime


class User(TypedDict):
    id: int
    tg_id: int
    tg_username: str
    group: str
    creation_time: datetime
