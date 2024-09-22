from abc import abstractmethod
from typing import Any

from asyncpg import Pool


class TableBase:
    _pool: Pool

    def __init__(self, pool: Pool):
        self._pool = pool

    @staticmethod
    def _parse_int(value: str | int | Any) -> int | None:
        if isinstance(value, int):
            return value

        if isinstance(value, str):
            if value.isdigit():
                return int(value)

        return None

    @abstractmethod
    async def initialize(self) -> None:
        pass

    async def execute(self,
                      command: str,
                      *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      executemany: bool = False) -> Any:
        if self._pool is None:
            return

        async with self._pool.acquire() as connection:
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                    if result:
                        result=dict(result)
                elif executemany:
                    result = await connection.executemany(command, *args)
                else:
                    result = await connection.execute(command, *args)

            return result
