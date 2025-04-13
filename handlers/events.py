from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
import json

router = Router()

# Системный промт один на весь диалог
SYSTEM_PROMPT = """
У тебя задача вести диалог по созданию события.

Твои действия:
1. Обнови JSON, добавив новый ключ (если это был ответ).
2. Если ещё есть незаполненные поля — задай новый вопрос.
3. Если всё заполнено — напиши "Готово" и отдай финальный JSON.
"""

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

    # Добавляем новый ввод пользователя
    chat_history.append({"role": "user", "content": user_input})

    # Добавляем текущий JSON в виде текста — GPT сам поймет контекст
    chat_history.append({
        "role": "user",
        "content": f"Текущий JSON: {json.dumps(event_data, ensure_ascii=False)}"
    })

    response = get_gpt_response(chat_history)

    # Удаляем сообщение с JSON, чтобы история была чище
    chat_history.pop()

    # Добавляем ответ GPT
    chat_history.append({"role": "assistant", "content": response})

    if "Готово" in response:
        try:
            extracted_json = response.split("Готово")[-1].strip()
            event_data = json.loads(extracted_json)

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

        except Exception as e:
            await message.answer(f"Ошибка при создании события: {str(e)}")
    else:
        await state.update_data(event_data=event_data, chat_history=chat_history)
        await message.answer(response)
