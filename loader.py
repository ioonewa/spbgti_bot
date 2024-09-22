from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database import Database

from config import *

# Телеграм Бот - Основной
bot = Bot(
    token=MAIN_BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
dispatcher = Dispatcher()

# БД
database = Database(
    main_credentials
)