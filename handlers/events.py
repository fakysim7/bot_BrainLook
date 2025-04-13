from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_event_creation_response  # обновлённый импорт
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
import json

router = Router()

@router.callback_query(lambda c: c.data == "events")
async def start_event_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Начинаем диалог с GPT, создаём пустой JSON для данных
    event_data = {}

    # Получаем первый вопрос
    response = get_event_creation_response(event_data)

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

    # Получаем ответ от GPT с обновлением JSON
    response = get_event_creation_response(event_data, user_input)

    if "Готово" in response:
        try:
            event_json_part = response.split("Готово")[-1].strip()
            event_data = json.loads(event_json_part)

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
        except json.JSONDecodeError:
            await message.answer("Ошибка при обработке итоговых данных. Попробуй ещё раз.")
    else:
        # Попробуем обновить данные, если GPT их уже добавил
        try:
            if "{" in response and "}" in response:
                json_text = response[response.find("{"):response.rfind("}") + 1]
                new_data = json.loads(json_text)
                event_data.update(new_data)
        except Exception:
            pass  # Если не получилось — просто продолжаем

        await state.update_data(event_data=event_data)
        await message.answer(response)
