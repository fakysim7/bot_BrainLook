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
Твоя задача - помощь в создании событий.
Собирая данные ты должен сохранять формат csv.
очередность:
Название, дата, время, место, адрес, гости.
Ты так же можешь сохранять доп.инфу, если считаешь, что нужно больше данных, сохраняй их в скобках в колонку custom. Спрашивай не напрямую, веди текучий диалог. 
Анализируй дату и уточняй время, если оно не указано в 24ч. формате
Сообщения короткие, дружелюбные. Можешь использовать эмодзи

По завершению вопросов - собирай csv и отправляй его мне. дату и время форматируй в timestamp.
Начнем с вопроса о названии
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
