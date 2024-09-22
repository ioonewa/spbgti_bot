from datetime import datetime
from database.types import Lessons

from babel.dates import format_date

from config import LIFETIME_INDEX

from loader import database

import locale

from .designations import *

async def get_week_type(date: datetime) -> str:
    # Неправильная неделя, но такой ВУЗ :)
    if date.isocalendar().week % 2 != 0:
        return "even"
    else:
        return "odd"

def get_format_date(date: datetime):
    # Устанавливаем русскую локализацию для работы с датами
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    
    # Получаем день недели и дату в родительном падеже
    day_of_week = date.strftime('%A')  # Полное название дня недели
    day_and_month = format_date(date, "d MMMM", locale='ru_RU')  # Число и месяц в родительном падеже

    # Собираем итоговую строку
    russian_date = f"{day_of_week} | {day_and_month}"

    return russian_date.title()
    
def get_weekday(date: datetime):
    weekday_number = date.weekday()
    
    return days_of_week[weekday_number]

def get_icons(lesson_type: str) -> str:
        icons = []
        
        if lesson_type:
            lesson_type = lesson_type.lower()
            if "лекц" in lesson_type:
                icons.append(lesson_type_icons.get("Лекция"))
            if "прак" in lesson_type:
                icons.append(lesson_type_icons.get("Практика"))
            if "лаб" in lesson_type:
                icons.append(lesson_type_icons.get("Лабораторная"))
            if "к/п" in lesson_type or "к\\п" in lesson_type:
                icons.append(lesson_type_icons.get("К/П"))
            if "к/р" in lesson_type or "к\\р" in lesson_type:
                icons.append(lesson_type_icons.get("К/Р"))

        return " / ".join(icons)

import json

def replace_nth_space(s, n, new_char) -> str:
    count = 0
    s_list = list(s)  # Преобразуем строку в список, чтобы можно было изменять символы

    for i, char in enumerate(s_list):
        if char == ' ':
            count += 1
            if count == n:
                s_list[i] = new_char
                break  # Прекращаем поиск после замены

    return ''.join(s_list)  # Преобразуем список обратно в строку

async def format_timetable(lessons: dict[Lessons]) -> str:
    lessons_list = []
    for lesson_number, lesson in lessons.items():
        lesson: Lessons
        # Иконки показывают тип занятия рядом с названием (Практика, Лекция, Лабораторная, К/П, К/Р)
        icons = get_icons(lesson['lesson_type'])
        
        lesson['name'] = lesson['name'].capitalize()
        
        # Иначе иконки слазят на другую строку и некрасиво
        # Нужно доработать
        if len(lesson['name']) > 25:
            if lesson['name'].count(" ") <= 2:
                lesson['name'] = lesson['name'].replace(" ", "\n\t\t\t\t", 1)
            elif lesson['name'].count(" ") > 2 and lesson['name'].count(" ") < 4:
                lesson['name'] = replace_nth_space(lesson['name'], 2, "\n\t\t\t\t")
            elif lesson['name'].count(" ") >= 4:
                lesson['name'] = replace_nth_space(lesson['name'], 2, "\n\t\t\t\t")
                lesson['name'] = replace_nth_space(lesson['name'], 4, "\n\t\t\t\t")
            
            
        base_lesson = [
            f"<b>{lesson_number}. {lesson['name']}</b> {icons}",
            lessons_time.get(lesson_number, "❌")
        ]   
        if lesson['tutor']:
            base_lesson.append(f"<code>{lesson['tutor']}</code>")
        if lesson['location']:
            base_lesson.append(f"📍 {lesson['location']}")
        lessons_list.append("\n\t\t\t\t".join(base_lesson))
    
    return "\n\n".join(lessons_list)

def get_header(date: datetime) -> str:
        format_date = get_format_date(date)
        if date.date() == datetime.now().date():
            format_date = f'📌 {format_date}'
        else:
            format_date = f'🔘 {format_date}'
        
        return format_date
 
async def get_day_timetable(group: str, date: datetime):
    week_type = await get_week_type(date)
    # Получить расписание для группы
    timetable_data = await database.schedule.get_lessons_for_day(
        group=group,
        week_type=week_type,
        day=get_weekday(date),
        lifetime_index=LIFETIME_INDEX
    )
    
    if timetable_data:
        timetable = await format_timetable(json.loads(timetable_data))
    else:
        timetable = "\t\t\t\t<code>Занятий нет</code>"
    
    # Получить шапку расписания — 📌 Четверг | 7 Января
    header = get_header(date)
    
    week_icon = week_types.get(week_type).split(" ")[0]
    
    return f"{week_icon} <b>Группа {group}</b>\n\n{header}\n\n{timetable}"
    
async def get_week_timetable(group: str, week_type: str):
    result = []

    # Перебираем дни недели и получаем расписание на каждый день
    for day in days_of_week.values():
        timetable_data = await database.schedule.get_lessons_for_day(
            group=group,
            week_type=week_type,
            day=day,
            lifetime_index=LIFETIME_INDEX
        )
        
        if timetable_data:
            timetable = await format_timetable(json.loads(timetable_data))
        else:
            timetable = "<code>Занятий нет</code>"
        
        rus_day = rus_days_of_week[day]
        result.append(f"🔘 {rus_day}\n\n{timetable}")
    
    timetable = "\n\n".join(result)
    
    week_icon = week_types.get(week_type).split(" ")[0]
    
    return f"{week_icon} <b>Группа {group}</b>\n\n{timetable}"