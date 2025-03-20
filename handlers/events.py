from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard

router = Router()



@router.callback_query(lambda c: c.data == "events")
async def start_event_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(EventCreationStates.waiting_for_data)
    await state.update_data(collected_data={})  # Инициализация пустого словаря для данных
    await ask_next_question(callback.message, state)

async def ask_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    collected_data = data.get("collected_data", {})

    # Формируем промпт для GPT
    prompt = f"""
    Чат, ты выступаешь в роли ассистента, помогаешь с созданием события через бота.
    Уже собраны следующие данные: {collected_data}.
    Сгенерируй следующий вопрос для пользователя, чтобы собрать недостающие данные.
    Необходимые пункты:
    "Название", "Дата", "Время", "Место", "Тип события", "Гости".
    """

    # Получаем ответ от GPT
    assistant_response = get_gpt_response(prompt)

    # Отправляем вопрос пользователю
    await message.answer(assistant_response)

@router.message(EventCreationStates.waiting_for_data)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text
    data = await state.get_data()
    collected_data = data.get("collected_data", {})

    # Формируем промпт для GPT, чтобы определить, какой ключ обновить
    prompt = f"""
    Чат, ты выступаешь в роли ассистента, помогаешь с созданием события через бота.
    Пользователь ввел следующее: {user_input}.
    Уже собраны следующие данные: {collected_data}.
    Определи, какой ключ ("Название", "Дата", "Время", "Место", "Тип события", "Гости") нужно обновить, и верни его.
    """

    # Получаем ответ от GPT
    key_to_update = get_gpt_response(prompt)

    # Обновляем данные
    collected_data[key_to_update] = user_input
    await state.update_data(collected_data=collected_data)

    # Проверяем, все ли данные собраны
    required_keys = ["Название", "Дата", "Время", "Место", "Тип события"]
    if all(key in collected_data for key in required_keys):
        await create_event(
            title=collected_data.get("Название"),
            date=collected_data.get("Дата"),
            time=collected_data.get("Время"),
            place=collected_data.get("Место"),
            event_type=collected_data.get("Тип события"),
            guests=collected_data.get("Гости")
        )
        await state.clear()
        await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)
    else:
        await ask_next_question(message, state)

@router.message(lambda message: message.text == "Выход в меню")
async def return_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=inline_keyboard)
