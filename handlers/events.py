#handlers/events.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
from database.connection import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import json
import dateparser
import re

router = Router()

@router.callback_query(lambda c: c.data == "events")
async def start_event_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    user_message = {"role": "user", "content": "Хочу создать новое событие."}
    messages = [user_message]

    response = get_gpt_response(messages)
    messages.append({"role": "assistant", "content": response})

    await state.update_data(event_data={}, chat_history=messages)
    await state.set_state(EventCreationStates.collecting_data)

    await callback.message.answer(response)


@router.message(EventCreationStates.collecting_data)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    data = await state.get_data()
    event_data = data.get("event_data", {})
    chat_history = data.get("chat_history", [])

    # Добавляем текущий ввод в историю
    chat_history.append({"role": "user", "content": user_input})

    # Обновлённый system prompt для GPT
    system_prompt = f"""
    Ты помогаешь создать событие. Текущие данные:
    {json.dumps(event_data, ensure_ascii=False)}
    
    Правила:
    1. Добавляй полученные данные в JSON
    2. Спрашивай по одному вопросу за раз
    3. Когда все данные собраны, верни JSON в ```json ``` без дополнительного текста
    4. Обязательные поля: название, дата, время, место, цель
    """

    try:
        # Получаем ответ от GPT
        response = get_gpt_response(
            [{"role": "system", "content": system_prompt}] + chat_history
        )
        
        # Проверяем, содержит ли ответ завершённый JSON
        if "```json" in response:
            json_match = re.search(r"```json\s*({.*?})\s*```", response, re.DOTALL)
            if json_match:
                event_data = json.loads(json_match.group(1))
                
                # Проверяем обязательные поля
                required_fields = ["название", "дата", "время", "место", "цель"]
                if all(field in event_data for field in required_fields):
                    # Сохраняем событие
                    async with get_async_session() as session:
                        await create_event(
                            session=session,
                            title=event_data["название"],
                            date=event_data["дата"],
                            time=event_data["время"],
                            location=event_data["место"],
                            purpose=event_data["цель"],
                            participants=event_data.get("участники", 0),
                            notes=event_data.get("примечания", "")
                        )
                    
                    await state.clear()
                    await message.answer(
                        "Событие успешно создано! ✅\n"
                        f"Название: {event_data['название']}\n"
                        f"Дата: {event_data['дата']}\n"
                        f"Место: {event_data['место']}",
                        reply_markup=inline_keyboard
                    )
                    return
                else:
                    missing = [f for f in required_fields if f not in event_data]
                    await message.answer(f"Не хватает данных: {', '.join(missing)}")
            else:
                await message.answer("Не удалось обработать данные события")
        
        # Если JSON не завершён, продолжаем диалог
        await state.update_data(event_data=event_data, chat_history=chat_history)
        await message.answer(response)

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        await state.update_data(chat_history=chat_history)
        await message.answer(response)
