from ._base import TableBase
from ..types import Lessons

from typing import List

class ScheduleTable(TableBase):
    async def initialize(self):
        await self.execute(
            'create table if not exists schedule('
            '   study_group text,'
            '   week_type text,'
            '   day text,'
            '   lessons JSONB,'
            '   lifetime_index integer,'
            '   creation_time timestamp default current_timestamp,'
            '   unique (study_group, week_type, lifetime_index, day)'
            ')'
        )

    async def add(self, group: str, week_type: str, day: str, lessons: dict, lifetime_index: int):
        await self.execute(
            'insert into schedule '
            '(study_group, week_type, day, lessons, lifetime_index) '
            'values ($1,$2,$3,$4,$5) '
            'on conflict (study_group, week_type, lifetime_index, day) '
            'do update set lessons = $4',
            group, week_type, day, lessons, lifetime_index
        )
    
    async def get_lessons_for_day(self, group: int, week_type: str, day: str, lifetime_index: int) -> Lessons | None:
        return await self.execute(
            'select lessons from schedule where study_group = $1 and week_type = $2 and day = $3 and lifetime_index = $4',
            group, week_type, day, lifetime_index,
            fetchval=True
        )
    
    async def get_lessons_for_week(self, group: int, week_type: str, lifetime_index: int) -> List[Lessons] | None:
        return await self.execute(
            'select lessons from schedule where study_group = $1 and week_type = $2 and lifetime_index = $3',
            group, week_type, lifetime_index,
            fetch=True
        )