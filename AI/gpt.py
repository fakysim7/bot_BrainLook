# openai/gpt.py
from openai import OpenAI  # Импортируем новый клиент OpenAI
from config import Config

# Инициализация клиента OpenAI
client = OpenAI(api_key=Config.OPENAI_API_KEY)

def get_gpt_response(prompt: str) -> str:
    try:
        # Используем chat.completions.create для GPT-3.5/GPT-4
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Указываем модель
            messages=[
                {"role": "user", "content": prompt}  # Передаем промпт
            ] # Ограничиваем количество токенов
        )
        # Возвращаем текст ответа
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Обработка ошибок
        return f"Ошибка при запросе к OpenAI: {str(e)}"