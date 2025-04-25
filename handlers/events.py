from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
import json
import csv
import os

router = Router()


CSV_FILE_PATH = "events.csv"

# Создание CSV-файла с заголовками, если он ещё не существует
if not os.path.exists(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Название", "Дата", "Время", "Место", "Адрес", "Тип события", "Гости"])


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

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({
        "role": "user",
        "content": f"Текущий JSON: {json.dumps(event_data, ensure_ascii=False)}"
    })

    response = get_gpt_response(chat_history)

    chat_history.pop()
    chat_history.append({"role": "assistant", "content": response})

    if "Готово" in response:
        try:
            extracted_json = response.split("Готово")[-1].strip()
            event_data = json.loads(extracted_json)

            with open(CSV_FILE_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    event_data.get("Название"),
                    event_data.get("Дата"),
                    event_data.get("Время"),
                    event_data.get("Место"),
                    event_data.get("Адрес", ""),
                    event_data.get("Тип события"),
                    ", ".join(event_data.get("Гости", []))
                ])

            await state.clear()
            await message.answer("Событие успешно создано и сохранено в CSV!")
        except Exception as e:
            await message.answer(f"Ошибка при сохранении события: {str(e)}")
    else:
        await state.update_data(event_data=event_data, chat_history=chat_history)
        await message.answer(response)
