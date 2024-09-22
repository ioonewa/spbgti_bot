import logging
import asyncpg
from asyncpg import Pool

from .tables import *
from database.types import PostgresCredentials

logger = logging.getLogger(__name__)


class Database:
    _pool: Pool
    _credentials: PostgresCredentials

    users: UsersTable
    schedule: ScheduleTable


    def __init__(self, credentials: PostgresCredentials):
        self._credentials = credentials
        
    async def initialize(self):
        logger.debug('Initializing pool.')
        self._pool = await asyncpg.create_pool(**self._credentials)
        logger.info('Pool initialized')
        
        logger.debug('Initializing modules')

        self.users = UsersTable(self._pool)
        await self.users.initialize()
        
        self.schedule = ScheduleTable(self._pool)
        await self.schedule.initialize()

        logger.info('Modules initialized.')