from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError

from datetime import datetime, timedelta


from typing import List

from loader import database
from ..utils import get_day_timetable, get_week_type, get_week_timetable, get_legend, get_format_date, week_types

import logging
import config

from math import ceil