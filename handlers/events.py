from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard

router = Router()

# Список обязательных полей и их порядок
REQUIRED_FIELDS = [
    "Название",
    "Дата", 
    "Время",
    "Место",
    "Тип события"
]

@router.callback_query(lambda c: c.data == "events")
async def start_event_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    # Инициализируем данные и запоминаем текущий шаг
    await state.update_data({
        'collected_data': {},
        'current_field_index': 0
    })
    await state.set_state(EventCreationStates.waiting_for_date)
    await ask_for_field(callback.message, state)

async def ask_for_field(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_index = data['current_field_index']
    
    # Проверяем, есть ли еще поля для заполнения
    if current_index < len(REQUIRED_FIELDS):
        current_field = REQUIRED_FIELDS[current_index]
        
        # Формируем вопрос для текущего поля
        prompt = f"""
        Сгенерируй вопрос для пользователя, чтобы получить информацию для поля "{current_field}".
        Будь дружелюбным и конкретным. Примеры:
        - Для "Название": "Как назовем ваше событие?"
        - Для "Дата": "На какую дату планируем событие? (например, 15.06.2023)"
        """
        
        question = get_gpt_response(prompt)
        await message.answer(question)
    else:
        # Все обязательные поля заполнены
        await handle_completed_data(message, state)

@router.message(EventCreationStates.waiting_for_date)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    data = await state.get_data()
    current_index = data['current_field_index']
    collected_data = data['collected_data']
    
    # Проверяем, что ввод не пустой
    if not user_input:
        await message.answer("Пожалуйста, введите корректные данные.")
        return
    
    # Получаем текущее поле и сохраняем ответ
    current_field = REQUIRED_FIELDS[current_index]
    collected_data[current_field] = user_input
    
    # Обновляем состояние
    await state.update_data({
        'collected_data': collected_data,
        'current_field_index': current_index + 1
    })
    
    # Переходим к следующему полю или завершаем
    if current_index + 1 < len(REQUIRED_FIELDS):
        await ask_for_field(message, state)
    else:
        await handle_completed_data(message, state)

async def handle_completed_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    collected_data = data['collected_data']
    
    # Спрашиваем про необязательные поля
    if "Гости" not in collected_data:
        prompt = """Нужно ли указать список гостей? (Да/Нет)"""
        await message.answer(prompt)
        await state.set_state(EventCreationStates.waiting_for_guests)
    else:
        await save_and_finish(message, state, collected_data)

@router.message(EventCreationStates.waiting_for_guests)
async def process_guests(message: types.Message, state: FSMContext):
    user_input = message.text.strip().lower()
    data = await state.get_data()
    collected_data = data['collected_data']
    
    if user_input == 'да':
        await message.answer("Введите список гостей (через запятую):")
        await state.set_state(EventCreationStates.waiting_for_guests)
    else:
        collected_data['Гости'] = None
        await save_and_finish(message, state, collected_data)

@router.message(EventCreationStates.waiting_for_guests)
async def process_guests_list(message: types.Message, state: FSMContext):
    guests = [g.strip() for g in message.text.split(',')]
    data = await state.get_data()
    collected_data = data['collected_data']
    collected_data['Гости'] = guests
    await save_and_finish(message, state, collected_data)

async def save_and_finish(message: types.Message, state: FSMContext, collected_data: dict):
    # Сохраняем событие в БД
    await create_event(
        title=collected_data.get("Название"),
        date=collected_data.get("Дата"),
        time=collected_data.get("Время"),
        place=collected_data.get("Место"),
        address=None,  # Добавляем address=None, если поле необязательное
        event_type=collected_data.get("Тип события"),
        guests=collected_data.get("Гости")
    )
    
    await state.clear()
    await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)


@router.message(lambda message: message.text == "Выход в меню")
async def return_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=inline_keyboard)
