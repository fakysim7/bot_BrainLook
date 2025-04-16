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
    chat_history = data.get("chat_history", [])
    event_data = data.get("event_data", {})

    # Добавляем пользовательский ввод в историю
    chat_history.append({"role": "user", "content": user_input})

    try:
        # Улучшенный prompt для GPT
        system_prompt = """
        Ты помогаешь создать событие. Анализируй ввод пользователя и:
        1. Если это ответ на предыдущий вопрос - добавь в JSON
        2. Если данных недостаточно - задай следующий вопрос
        3. Будь терпимым к формату ввода
        4. Не начинай диалог заново при ошибках
        Текущие данные: {current_data}
        """.format(current_data=json.dumps(event_data, ensure_ascii=False))

        response = get_gpt_response([{"role": "system", "content": system_prompt}] + chat_history)
        chat_history.append({"role": "assistant", "content": response})

        if "Готово" in response:
            # Обработка завершения
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if json_match:
                event_data = json.loads(json_match.group(1))
                
                # Сохраняем событие
                async with get_async_session() as session:
                    await create_event(
                        session=session,
                        title=event_data.get("Название"),
                        date=event_data.get("Дата"),
                        duration=event_data.get("Длительность"),
                        # остальные поля
                    )
                
                await state.clear()
                await message.answer("Событие создано!", reply_markup=inline_keyboard)
            else:
                await message.answer("Не удалось извлечь данные события")
        else:
            await state.update_data(event_data=event_data, chat_history=chat_history)
            await message.answer(response)

    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
        await state.update_data(chat_history=chat_history)  # Не сбрасываем полностью
        await message.answer(response)
