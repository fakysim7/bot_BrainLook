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
    event_data = data.get("event_data", {})

    # Формируем запрос к GPT
    prompt = f"""
    Веди диалог по созданию события.
    Уже собранные данные (JSON): {json.dumps(event_data, ensure_ascii=False)}
    Пользователь ответил: "{user_input}".
    
    1. Обнови JSON, добавив новый ключ (если это был ответ).
    2. Если заполнены все основные 5 вопросов — спроси, хочет ли пользователь добавить еще данные.
    3. Если все заполнено и пользователь не хочет добавлять, напиши "Готово" и верни JSON отдельно.
    
    Отвечай в формате:
    {{ "updated_json": {{ ... }}, "next_question": "..." }}
    """

    response = get_gpt_response(prompt)

    try:
        response_data = json.loads(response)
        event_data = response_data["updated_json"]
        next_question = response_data["next_question"]
    except (json.JSONDecodeError, KeyError):
        await message.answer("Произошла ошибка при обработке данных. Попробуйте снова.")
        return

    # Проверяем завершение
    if next_question == "Готово":
        # Записываем событие в БД
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
        # Обновляем состояние и продолжаем диалог
        await state.update_data(event_data=event_data)
        await message.answer(next_question)

