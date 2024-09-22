from ._base import TableBase
from ..types import User

from typing import List

class UsersTable(TableBase):
    async def initialize(self):
        await self.execute(
            'create table if not exists users('
            '   id serial primary key,'
            '   tg_id bigint unique,'
            '   tg_username text,'
            '   study_group text,'
            '   creation_time timestamp default current_timestamp'
            ')'
        )

    async def add(self, tg_id: int, tg_username: str):
        await self.execute(
            'insert into users (tg_id, tg_username) VALUES ($1,$2) '
            'on conflict(tg_id) do nothing',
            tg_id, tg_username
        )
    
    async def get(self, tg_id: int | str) -> User | None:
        return await self.execute(
            'select * from users where tg_id = $1',
            self._parse_int(tg_id),
            fetchrow=True
        )
    
    async def set_group(self, tg_id: int | str, group: str):
        await self.execute(
            'update users set study_group = $1 where tg_id = $2',
            group, self._parse_int(tg_id)
        )
        
    async def get_group(self, tg_id: int | str) -> str | None:
        return await self.execute(
            'select study_group from users where tg_id = $1',
            self._parse_int(tg_id),
            fetchval=True
        )
        
    async def get_students_from_group(self, group: str) -> List[User]:
        return await self.execute(
            'select * from users where study_group = $1',
            group,
            fetch=True
        )
        
    async def count_students_in_group(self, group: str) -> int:
        return await self.execute(
            'select count(*) from users where study_group = $1',
            group,
            fetchval=True
        )
        
    async def get_all_groups(self) -> List[str]:
        return await self.execute(
            'select distinct study_group from users',
            fetch=True
        )
        
    async def count(self) -> int:
        return await self.execute(
            'select count(*) from users',
            fetchval=True
        )