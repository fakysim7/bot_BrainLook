# openai/gpt.py
from openai import OpenAI  # Импортируем новый клиент OpenAI
from config import Config

# Инициализация клиента OpenAI
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# def get_gpt_response(prompt: str) -> str:
#     try:
#         # Используем chat.completions.create для GPT-3.5/GPT-4
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # Указываем модель
#             messages=[
#                 {"role": "system", "content": prompt}  # Передаем промпт
#             ] # Ограничиваем количество токенов
#         )
#         # Возвращаем текст ответа
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         # Обработка ошибок
#         return f"Ошибка при запросе к OpenAI: {str(e)}"



# Хранилище чатов: ключ — имя состояния, значение — список сообщений
chat_states = {
    "default": [
        {"role": "system", "content": "Ты — дружелюбный помощник."}
    ]
}

def get_gpt_response(prompt: str, state: str = "default") -> str:
    try:
        # Добавляем новое сообщение от пользователя
        chat_states[state].append({"role": "user", "content": prompt})

        # Запрос к GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_states[state]
        )

        # Сохраняем ответ ассистента в историю
        reply = response.choices[0].message.content.strip()
        chat_states[state].append({"role": "assistant", "content": reply})

        return reply
    except Exception as e:
        return f"Ошибка при запросе к OpenAI: {str(e)}"

def reset_chat_state(state: str = "default", system_prompt: str = "Ты — дружелюбный помощник."):
    chat_states[state] = [{"role": "system", "content": system_prompt}]
