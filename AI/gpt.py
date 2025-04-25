#AI/gpt.py
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# SYSTEM_PROMPT = """
# У тебя задача вести диалог по созданию события. 

# Твои действия:
# 1. Обнови JSON, добавив новый ключ (если это был ответ).
# 2. Если ещё есть незаполненные поля — задай новый вопрос.
# 3. Если всё заполнено — напиши "Готово" и отдай финальный JSON.
# """


SYSTEM_PROMPT = """
У тебя задача вести диалог по созданию события. 
Задавай только по одному вопросу по очереди.

Твои действия:

1. Задай вопрос пользователю (учитывай предыдущие вопросы, если они есть)
2. Обнови JSON, добавив новый ключ (если это был ответ) Никогда не показывай ключ пользователю.
3. Если ещё есть незаполненные поля — задай новый вопрос.
4. Если заполнено минимум 7 полей, указанных как обязательные (если чувствуешь, что нужно добавить кастомные - добавляй) — напиши "Готово" и вышли все детали события в чат.
5. Если пользователь вводит что-то неправильно — исправляй ошибку и сохраняй корректну версию.
"""

def get_gpt_response(messages: list[dict]) -> str:
    try:
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages  # ✅ Списки объединяются правильно

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=full_messages
        )

        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        return f"Ошибка при запросе к OpenAI: {str(e)}"
