from typing import TypedDict


class PostgresCredentials(TypedDict):
    host: str
    database: str
    user: str
    password: str
