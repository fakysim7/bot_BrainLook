from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from utils.states import EventCreationStates
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
import json

router = Router()

@router.message(EventCreationStates.collecting_data)
async def process_user_input(message: types.Message, state: FSMContext):
    user_input = message.text.strip()

    # Получаем текущее состояние
    data = await state.get_data()
    event_data = data.get('event_data', {})

    # Основные 5 вопросов
    required_fields = ["Название", "Дата", "Время", "Место", "Тип события"]
    missing_fields = [field for field in required_fields if field not in event_data]

    if missing_fields:
        next_question = missing_fields[0]
    else:
        next_question = "Дополнительные данные"  # После основных вопросов

    # Формируем запрос к GPT
    prompt = f"""
    Веди диалог по созданию события.
    Уже собранные данные (JSON): {json.dumps(event_data, ensure_ascii=False)}
    Пользователь ответил: "{user_input}".
    
    1. Обнови JSON, добавив новый ключ (если это был ответ).
    2. Если заполнены все основные 5 вопросов — спроси, хочет ли пользователь добавить еще данные.
    3. Если все заполнено и пользователь не хочет добавлять, напиши "Готово" и верни JSON.
    
    Следующий вопрос: "{next_question}"
    """
    
    response = get_gpt_response(prompt)

    # Проверяем завершение
    if "Готово" in response:
        json_part = response.split("Готово")[-1].strip()

        # Проверка валидности JSON
        try:
            event_data = json.loads(json_part)
        except json.JSONDecodeError:
            await message.answer("Произошла ошибка при обработке данных. Попробуйте снова.")
            return

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

        # Убираем логи и оставляем только понятный текст для пользователя
        clean_response = response.split("\n", 1)[-1]  # Убираем возможные служебные строки
        await message.answer(clean_response)
