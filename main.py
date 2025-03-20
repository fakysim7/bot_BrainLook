from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # Импортируем DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import Config
from handlers import router
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота с использованием DefaultBotProperties
bot = Bot(
    token=Config.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Указываем parse_mode здесь
)

# Инициализация диспетчера
dp = Dispatcher()

# Подключение роутеров
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())