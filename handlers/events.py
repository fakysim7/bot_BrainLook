from aiogram import types
from aiogram import Router
from AI.gpt import get_gpt_response
from database.crud import create_event
from keyboards.main_menu import inline_keyboard
import re

router = Router()

def extract_keys(response):
    keys = {}
    # Регулярное выражение для поиска ключей
    pattern = r'"Ключ: (.*?)"'
    matches = re.findall(pattern, response)
    for match in matches:
        # Разделяем ключ и значение
        if ": " in match:
            key, value = match.split(": ", 1)
            keys[key] = value
    return keys

@router.message()
async def handle_message(message: types.Message):
    user_message = message.text
    token_max = 100

    # Формируем промпт для OpenAI
    prompt = f"""
    Чат, ты выступаешь в роли ассистента, помогаешь с созданием события через бота.
    Мне нужно, чтобы ты вел простой диалог, используя до {token_max} токенов на ответ, собирая данные с пользователя по мере разговора.
    В то же время в ответ вставляй ключи, помечая их так: "Ключ: Название пункта" именно с кавычками.
    Стартуешь ты с названия и задаешь наводящие вопросы (но название ты ждешь как сообщение, не спрашиваешь о нем).
    Необходимые пункты:
    "Дата", "Время", "Место" (после указания спрашивай, надо ли указывать адрес и создавай "Адрес"), "Тип" события (например: поход с друзьями, мероприятие, форум и так далее (думай сам, отталкиваясь от названия). Если тип события подразумевает наличие определенного кол-ва людей, которых ты можешь выбирать сам (ресторан, к примеру) - "Гости".

    Текущий диалог:
    Пользователь: {user_message}
    Ассистент:
    """

    # Получаем ответ от OpenAI
    assistant_response = get_gpt_response(prompt)

    # Отправляем ответ пользователю
    await message.answer(assistant_response)

    # Извлекаем ключи из ответа ассистента
    keys = extract_keys(assistant_response)

    # Сохраняем данные в базу данных
    if keys:
        await create_event(
            title=keys.get("Название"),
            date=keys.get("Дата"),
            time=keys.get("Время"),
            place=keys.get("Место"),
            address=keys.get("Адрес"),
            event_type=keys.get("Тип"),
            guests=keys.get("Гости")
        )

@router.callback_query(lambda c: c.data == "events")
async def get_button_event(callback: types.CallbackQuery):
    # Убираем "часики" у кнопки
    await callback.answer()

    # Отправляем сообщение о начале создания события
    await callback.message.edit_text("Создание события")

    # Запускаем диалог с пользователем
    await handle_message(callback.message)

@router.message(lambda message: message.text == "Выход в меню")
async def return_to_menu(message: types.Message):
    await message.edit_text("Вы вернулись в главное меню.", reply_markup=inline_keyboard)