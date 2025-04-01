from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
import json

router = Router()

@router.callback_query(lambda c: c.data == "events")
async def start_event_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    # Начинаем процесс создания события
    event_data = {
        "Название": None,
        "Дата": None,
        "Время": None,
        "Место": None,
        "Адрес": None,
        "Тип события": None,
        "Гости": []
    }

    prompt = """
    Ты — умный ассистент, который помогает пользователю создать событие. 
    Задавай вопросы один за другим, уточняя информацию.
    
    - Запоминай, что уже было спрошено.
    - Не задавай одни и те же вопросы.
    - Веди диалог плавно, поддерживая естественное общение.
    
    Начнем с первого вопроса: Как называется событие?
    """

    response = get_gpt_response(prompt)
    
    await state.update_data(event_data=event_data)
    await state.set_state(EventCreationStates.collecting_data)
    await callback.message.answer(response)

@router.message(EventCreationStates.collecting_data)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()

    # Получаем текущее состояние
    data = await state.get_data()
    event_data = data.get('event_data', {})

    # Определяем, какой ключ сейчас заполняется
    keys_order = ["Название", "Дата", "Время", "Место", "Адрес", "Тип события", "Гости"]
    current_key = next((key for key in keys_order if event_data.get(key) is None), None)

    if current_key:
        event_data[current_key] = user_input

    # Проверяем, есть ли ещё незаполненные поля
    next_key = next((key for key in keys_order if event_data.get(key) is None), None)

    if next_key:
        prompt = f"""
        Ты ведешь диалог для создания события. Вот что уже известно:
        {json.dumps(event_data, ensure_ascii=False, indent=2)}
        
        Спроси у пользователя {next_key.lower()}.
        """
        response = get_gpt_response(prompt)
        await state.update_data(event_data=event_data)
        await message.answer(response)
    else:
        # Все данные собраны, записываем в БД
        await create_event(
            title=event_data["Название"],
            date=event_data["Дата"],
            time=event_data["Время"],
            place=event_data["Место"],
            address=event_data["Адрес"],
            event_type=event_data["Тип события"],
            guests=event_data["Гости"]
        )

        await state.clear()
        await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)
