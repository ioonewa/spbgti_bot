import logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs/spbgti_bot.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s"
)

import asyncio

from loader import bot, dispatcher, database

from telegram_bot import routers
from aiogram.types import BotCommand

import os

async def main():
    """
    Main function to initialize the bot and start polling.
    """
    os.makedirs("logs", exist_ok=True)
    
    await database.initialize()
    
    await bot.set_my_commands(
        commands=[
            BotCommand(command="timetable", description="Расписание"),
            BotCommand(command="week", description="Вся неделя"),
            BotCommand(command="group", description="Выбрать группу")
        ]
    )
        
    for router in routers:
        dispatcher.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
