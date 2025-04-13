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

    # Получаем текущее состояние и уже собранные данные
    data = await state.get_data()
    event_data = data.get("event_data", {})

    # Формируем промпт для GPT
    prompt = f"""
Ты ассистент, помогающий пользователю пошагово создать событие.
Вот уже собранные данные (в JSON): {json.dumps(event_data, ensure_ascii=False)}.
Пользователь ответил: "{user_input}".

1. Обнови JSON с учётом ответа пользователя.
2. Если ещё есть незаполненные поля — задай следующий вопрос.
3. Если всё готово — напиши "Готово", а затем выведи итоговый JSON.
"""

    response = get_gpt_response(prompt)

    if "Готово" in response:
        try:
            # Извлекаем JSON после "Готово"
            json_part = response.split("Готово", 1)[-1].strip()
            updated_event_data = json.loads(json_part)

            # Сохраняем в БД
            await create_event(
                title=updated_event_data.get("Название"),
                date=updated_event_data.get("Дата"),
                time=updated_event_data.get("Время"),
                place=updated_event_data.get("Место"),
                address=updated_event_data.get("Адрес", None),
                event_type=updated_event_data.get("Тип события"),
                guests=updated_event_data.get("Гости", [])
            )

            await state.clear()
            await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)
        except json.JSONDecodeError:
            await message.answer("Ошибка при обработке итоговых данных. Попробуй ещё раз.")
    else:
        # Пробуем обновить JSON, если GPT уже частично добавил ключи
        try:
            # Пробуем вытащить словарь из текста, если он присутствует
            if "{" in response and "}" in response:
                json_text = response[response.find("{"):response.rfind("}") + 1]
                new_data = json.loads(json_text)
                event_data.update(new_data)
        except Exception:
            pass  # Если парсинг не удался — продолжаем с тем, что есть

        await state.update_data(event_data=event_data)
        await message.answer(response)
