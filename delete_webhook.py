from aiogram import Bot
from config import Config

async def delete_webhook():
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    await bot.delete_webhook()
    print("Webhook удален!")

if __name__ == '__main__':
    import asyncio
    asyncio.run(delete_webhook())