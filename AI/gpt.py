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
Создавай события с данными в формате CSV.
Очередность: название, дата, время, место, адрес, гости.
Доп. инфо в колонке custom.
Если время не в 24ч. формате, уточни. дата+время сохраняется в timestamp. 
Начнем с названия события. Сообщения короткие и дружелюбные
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
