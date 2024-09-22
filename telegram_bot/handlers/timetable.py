from .modules import *

router = Router()

def choose_faculty_kb() -> InlineKeyboardMarkup:
    available_list = config.groups["faculty"].keys()
    kb = []
    
    for faculty in available_list:
        kb.append([InlineKeyboardButton(
            text=faculty,
            callback_data=f"faculty_{faculty}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_course_kb(faculty: str) -> InlineKeyboardButton:
    available_list = config.groups["faculty"][faculty].keys()
    kb = []
    
    for course in available_list:
        kb.append([InlineKeyboardButton(
            text=course,
            callback_data=f"course_{course}_faculty_{faculty}"
        )])
        
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"faculty_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
    

def get_page_items(lst, page_number: int):
    start_index = (page_number - 1) * config.page_length
    end_index = start_index + config.page_length
    return lst[start_index:end_index]

empty_btn = InlineKeyboardButton(text=" ", callback_data="empty")

def group_slider(faculty: str, course: str, state_data: dict):
    kb: List[List[InlineKeyboardButton]] = []
    current_page = state_data.get("current_page", 1)
    
    last_page = ceil(len(config.groups["faculty"][faculty][course]) / config.page_length)
    page = get_page_items(
        lst=config.groups["faculty"][faculty][course],
        page_number=current_page
    )    
    
    if page:
        for group in page:
            kb.append([InlineKeyboardButton(text=group, callback_data=f"group_{group}")])
    else:
        kb.append([InlineKeyboardButton(text="Группы пока не добавлены", callback_data="faculty_menu")])
            
    base_slider = [
        InlineKeyboardButton(text="◀️", callback_data="groups_prev"),
        InlineKeyboardButton(text="▶️", callback_data="groups_next")   
    ]
    
    if (last_page == 1) or (last_page == 0):
        pass
    elif current_page == 1:
        base_slider[0] = empty_btn
        kb.append(base_slider)
    elif current_page == last_page:
        base_slider[1] = empty_btn
        kb.append(base_slider)
    else:
        kb.append(base_slider)
        
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"faculty_{faculty}")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.message(Command('start'))
async def start(message: Message):
    # Добавить пользоватея в бд
    await database.users.add(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username
    )
    
    await faculty_menu(message)

@router.message(Command('group'))
@router.callback_query(F.data == "faculty_menu")
async def faculty_menu(event: CallbackQuery | Message):
    text = "<b>Выберите ваш Факультет</b>"
    markup = choose_faculty_kb()

    if isinstance(event, Message):
        await event.answer(
            text=text,
            reply_markup=markup
        )
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=markup
        )

@router.callback_query(F.data.startswith('faculty_'))
async def group_menu(call: CallbackQuery, state: FSMContext):
    faculty = call.data.replace("faculty_", "")
    await state.set_data({"faculty": faculty})
    await call.message.edit_text(
        text=f"<b>Факультет {faculty} | Выберите ваш курс</b>",
        reply_markup=get_course_kb(faculty)
    )
    
@router.callback_query(F.data.startswith('course_'))
async def course_menu(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    faculty = state_data.get("faculty")
    
    if not faculty:
        await faculty_menu(call)
        return
    
    try:
        a, course, b, faculty = call.data.split("_")
    except ValueError:
        logging.error(f"Error in course_menu: {call.data}")
        await faculty_menu(call)
        return
    
    await state.set_data({"faculty": faculty, "course": course})
    await call.message.edit_text(
        text=f"<b>Факультет {faculty} | Выберите ваш Группу</b>",
        reply_markup=group_slider(faculty, course, state_data)
    )
        
@router.callback_query(F.data == "groups_prev")
@router.callback_query(F.data == "groups_next")
async def groups_next(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    faculty = state_data.get("faculty")
    course = state_data.get("course")
    
    if not (faculty or course):
        await faculty_menu(call)
        return
    
    current_page = state_data.get("current_page", 1)
    
    if call.data == "groups_next":
        state_data = await state.update_data({"current_page": current_page + 1})
    elif call.data == "groups_prev":
        state_data = await state.update_data({"current_page": current_page - 1})
    
    await call.message.edit_reply_markup(
        reply_markup=group_slider(faculty, course, state_data)
    )
    
async def day_timetable_kb(group: str, date: datetime) -> InlineKeyboardMarkup:
    next_day_str = (date + timedelta(days=1)).strftime("%Y-%m-%d")
    prev_day_str = (date - timedelta(days=1)).strftime("%Y-%m-%d")
    
    week_type = await get_week_type(date)

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"day_timetable_{prev_day_str}_group_{group}"),
            InlineKeyboardButton(text="➡️", callback_data=f"day_timetable_{next_day_str}_group_{group}")
        ],
        [InlineKeyboardButton(text="📌 Сегодня", callback_data=f"day_timetable_today_group_{group}")],
        [InlineKeyboardButton(text=week_types[week_type], callback_data=f"week_timetable_{week_type}_group_{group}")],
        [InlineKeyboardButton(text="ℹ️ Обозначения", callback_data="legend_on")]
    ])
    
async def week_timetable_kb(group: str, week_type: str) -> InlineKeyboardMarkup:
    if week_type == "odd":
        week_kb = [
            InlineKeyboardButton(text="▫️ Четная", callback_data=f"week_timetable_even_group_{group}"),
            InlineKeyboardButton(text="🔹 Нечетная", callback_data="odd_yet")
        ]
    elif week_type == "even":
        week_kb = [
            InlineKeyboardButton(text="🔸 Четная", callback_data="even_yet"),
            InlineKeyboardButton(text="▫️ Нечетная", callback_data=f"week_timetable_odd_group_{group}")
        ]
        
    return InlineKeyboardMarkup(inline_keyboard=[
        week_kb,
        [InlineKeyboardButton(text="📌 Сегодня", callback_data=f"day_timetable_today_group_{group}")],
        [InlineKeyboardButton(text="ℹ️ Обозначения", callback_data="legend_on")]
    ])

@router.callback_query(F.data.startswith('group_'))
async def choose_group(call: CallbackQuery, state: FSMContext):
    group = call.data.replace("group_", "")
    date = datetime.now()
    # Обновить группу в бд
    await database.users.set_group(
        tg_id=call.from_user.id,
        group=group
    )
    
    faculty_number = group[0]

    await call.message.edit_text(
        f'<b>Факультет {faculty_number} | Группа {group}</b>'
    )
    
    # Место для рекламы
    await call.message.answer(
        text=...
    )
    
    timetable = await get_day_timetable(group, date)
    timetable_kb = await day_timetable_kb(group, date)
    
    await call.message.answer(
        text=timetable,
        reply_markup=timetable_kb
    )
    
    await state.clear()
 
@router.message(Command('timetable'))  
@router.callback_query(F.data.startswith('day_timetable_'))
async def day_timetable(event: CallbackQuery | Message):
    # На выходе из этой конструкции, мы получаем две переменные date_str и group
    # Разница в способах получения
    if isinstance(event, CallbackQuery):
        date_str, group = event.data.replace("day_timetable_", "").replace("group_", "").split("_")    
    else:
        date_str = "today"
        group = await database.users.get_group(event.from_user.id)
        
    if not group:
        logging.info(f"User {event.from_user.id} doesn't have a group")
        await faculty_menu(event)
        return
        
    if date_str == "today":
        date = datetime.now()
    else:
        date = datetime.strptime(date_str, "%Y-%m-%d")
 
    timetable = await get_day_timetable(group, date)
    timetable_kb = await day_timetable_kb(group, date)
    
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(
                text=timetable,
                reply_markup=timetable_kb
            )
        except TelegramAPIError:
            today = get_format_date(datetime.now())
            await event.answer(f"Сегодня — {today}")
    elif isinstance(event, Message):
        await event.answer(
            text=timetable,
            reply_markup=timetable_kb
        )
            
            
@router.message(Command('week'))
@router.callback_query(F.data.startswith('week_timetable_'))
async def week_timetable(event: CallbackQuery | Message):
    if isinstance(event, CallbackQuery):
        week_type , group = event.data.replace("week_timetable_", "").replace("group_", "").split("_")
    elif isinstance(event, Message):
        group = await database.users.get_group(event.from_user.id)
        week_type = await get_week_type(datetime.now())
        
    if not group:
        logging.info(f"User {event.from_user.id} doesn't have a group")
        await faculty_menu(event)
        return
    
    timetable = await get_week_timetable(group, week_type)
    kb = await week_timetable_kb(group, week_type)
    
    if isinstance(event,CallbackQuery):
        try:
            await event.message.edit_text(
                text=timetable,
                reply_markup=kb
            )
        except TelegramAPIError as ex:
            await event.answer(f"Сейчас {week_types[week_type]}")
    elif isinstance(event, Message):
        await event.answer(
            text=timetable,
            reply_markup=kb
        )

        
@router.callback_query(F.data.endswith('_yet'))
async def yet(call: CallbackQuery):
    # Прикол, правда?
    await call.answer(
        text = {
            # if
            "even_yet": "Выбрана Четная неделя",
            "odd_yet": "Выбрана Нечетная неделя"
        }.get(call.data,
            # else
            "Странная кнопка"
        )
    )

@router.callback_query(F.data.startswith('legend_'))
async def legend_show(call: CallbackQuery):
    kb_copy = call.message.reply_markup.inline_keyboard.copy()
    definition_btn_index = None
    
    # Алгоритм поиска ряда с кнопкой "Обозначения"
    for btn_row in kb_copy:
        if len(btn_row) == 1:
            btn = btn_row[0]
            if "Обозначения" in btn.text:
                definition_btn_index = kb_copy.index(btn_row)
                break
    
    if call.data == "legend_on":
        legend = await get_legend(call.message.text)
        
        kb_copy[definition_btn_index] = [InlineKeyboardButton(text="✖️ Обозначения", callback_data="legend_off")]
        new_text=f'{call.message.html_text}\n\n\n{legend}'
    elif call.data == "legend_off":
        try:
            new_text = call.message.html_text.split("<b>Обозначения</b>")[0]
        except IndexError:
            new_text = call.message.html_text
        kb_copy[definition_btn_index] = [InlineKeyboardButton(text="ℹ️ Обозначения", callback_data="legend_on")]
        
    await call.message.edit_text(
        text=new_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_copy)
    )