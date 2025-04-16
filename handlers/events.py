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

    # Добавляем пользовательский ввод и текущий JSON в историю
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "user", "content": f"Текущий JSON: {json.dumps(event_data, ensure_ascii=False)}"})

    response = get_gpt_response(chat_history)
    chat_history.pop()  # Удаляем JSON из истории для чистоты
    chat_history.append({"role": "assistant", "content": response})

    if "Готово" in response:
        # Ищем JSON-блок в ответе (предпочтительно в ```json)
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        json_text = json_match.group(1) if json_match else response.split("Готово")[-1].strip()

        try:
            event_data = json.loads(json_text)

            # Автоматический парсинг даты и времени
            parsed_date = dateparser.parse(event_data.get("Дата", ""))
            parsed_time = dateparser.parse(event_data.get("Время", ""))

            if parsed_date:
                event_data["Дата"] = parsed_date.strftime("%Y-%m-%d")
            if parsed_time:
                event_data["Время"] = parsed_time.strftime("%H:%M")

            # Простая валидация
            required_fields = ["Название", "Дата", "Время", "Место", "Тип события"]
            missing = [field for field in required_fields if not event_data.get(field)]
            if missing:
                await message.answer(f"Не хватает полей: {', '.join(missing)}. Пожалуйста, укажи их.")
                await state.update_data(event_data=event_data, chat_history=chat_history)
                return

            # Сохранение в базу

            await create_event(
                session=session,
                title=event_data["Название"],
                date=event_data["Дата"],
                time=event_data["Время"],
                place=event_data["Место"],
                address=event_data.get("Адрес"),
                event_type=event_data["Тип события"],
                guests=event_data.get("Гости", [])
            )

            await state.clear()
            await message.answer("Событие успешно создано! Возвращаемся в главное меню.", reply_markup=inline_keyboard)

        except Exception as e:
            await message.answer(f"Ошибка при обработке данных или создании события: {str(e)}")
    else:
        await state.update_data(event_data=event_data, chat_history=chat_history)
        await message.answer(response)
