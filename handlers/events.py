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
    
    # Начинаем диалог с GPT, создаём пустой JSON для данных
    event_data = {}
    prompt = "Ты ведущий диалога для создания события. Сформулируй первый вопрос пользователю."
    
    response = get_gpt_response(prompt)
    
    # Сохраняем состояние
    await state.update_data(event_data=event_data)
    await state.set_state(EventCreationStates.collecting_data)
    
    await callback.message.answer(response)

@router.message(EventCreationStates.collecting_data)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    
    # Получаем текущее состояние
    data = await state.get_data()
    event_data = data.get('event_data', {})

    # Формируем новый промпт, передавая уже собранные данные
    prompt = f"""
    У тебя задача вести диалог по созданию события. 
    Уже собранные данные (JSON): {json.dumps(event_data, ensure_ascii=False)}
    Пользователь ответил: "{user_input}".
    
    Твои действия:
    1. Обнови JSON, добавив новый ключ (если это был ответ).
    2. Если ещё есть незаполненные поля — задай новый вопрос.
    3. Если всё заполнено — напиши "Готово" и отдай финальный JSON.
    """
    
    response = get_gpt_response(prompt)
    
    # Проверяем, завершено ли заполнение
    if "Готово" in response:
        # Извлекаем JSON с финальными данными
        event_data = json.loads(response.split("Готово")[-1].strip())

        # Записываем в БД
        await create_event(
            title=event_data.get("Название"),
            date=event_data.get("Дата"),
            time=event_data.get("Время"),
            place=event_data.get("Место"),
            address=event_data.get("Адрес", None),
            event_type=event_data.get("Тип события"),
            guests=event_data.get("Гости", [])
        )

        await state.clear()
        await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)
    else:
        # Продолжаем диалог
        await state.update_data(event_data=event_data)
        await message.answer(response)
